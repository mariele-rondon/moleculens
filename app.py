from flask import Flask, request, render_template, jsonify, Response, stream_with_context, url_for, redirect
import os
import subprocess
import io, base64
import json
import time
import threading
import queue
import uuid
import re
from werkzeug.utils import secure_filename
from rdkit import Chem
from rdkit.Chem import Draw, AllChem # NOVO: Importa AllChem para a geração 3D
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

app = Flask(__name__)
# ... (o resto da configuração inicial continua o mesmo) ...
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ACTIVE_TASKS = set()
PROCESS_LOCK = threading.Lock()


def generate_molecule_svg(mol):
    # ... (esta função continua a mesma da versão anterior) ...
    try:
        drawer = rdMolDraw2D.MolDraw2DSVG(-1, -1)
        drawOptions = drawer.drawOptions()
        drawOptions.clearBackground = False
        drawOptions.setAtomPalette({k: (0, 0, 0) for k in range(mol.GetNumAtoms())})
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg_matriz = drawer.GetDrawingText()
        scale_factor = 2.0
        width_match = re.search(r"width=['\"]([\d\.]+)[\w]*['\"]", svg_matriz)
        height_match = re.search(r"height=['\"]([\d\.]+)[\w]*['\"]", svg_matriz)
        svg_final = svg_matriz
        if width_match and height_match:
            original_width = float(width_match.group(1))
            original_height = float(height_match.group(1))
            new_width = original_width * scale_factor
            new_height = original_height * scale_factor
            svg_final = svg_matriz.replace(f"width='{width_match.group(0)[7:]}'", f"width='{new_width}px'")
            svg_final = svg_final.replace(f"height='{height_match.group(0)[8:]}'", f"height='{new_height}px'")
        return svg_final.replace('svg:', '')
    except Exception as e:
        print(f"Erro ao gerar SVG final: {e}")
        return ""


# --- NOVA FUNÇÃO PARA GERAR A ESTRUTURA 3D EM FORMATO SDF ---
def generate_3d_sdf(mol):
    """Gera uma conformação 3D da molécula e a retorna como uma string no formato SDF."""
    try:
        # Adiciona hidrogênios, essencial para uma boa estrutura 3D
        mol_with_h = Chem.AddHs(mol)
        # Gera a conformação 3D
        status = AllChem.EmbedMolecule(mol_with_h, AllChem.ETKDG())
        if status == -1: # Falha na geração da conformação
            return ""
        # Otimiza a geometria da molécula (opcional, mas recomendado)
        AllChem.UFFOptimizeMolecule(mol_with_h)
        # Converte a molécula 3D para o formato SDF (MolBlock)
        sdf_string = Chem.MolToMolBlock(mol_with_h)
        return sdf_string
    except Exception as e:
        print(f"Erro ao gerar SDF 3D: {e}")
        return ""
# ----------------------------------------------------------------

def run_osra_in_thread(cmd, result_queue):
    # ... (esta função continua a mesma) ...
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate(timeout=300)
        if process.returncode == 0 and stdout and stdout.strip():
            smiles_candidates = stdout.strip().split()
            valid_smiles_found = None
            for s_candidate in smiles_candidates:
                mol = Chem.MolFromSmiles(s_candidate)
                if mol:
                    valid_smiles_found = s_candidate
                    break
            if valid_smiles_found:
                contains_r_group = '*' in valid_smiles_found
                result_queue.put({'status': 'success', 'data': valid_smiles_found, 'contains_r_group': contains_r_group})
            else:
                raise ValueError("A imagem não pôde ser convertida em uma estrutura química válida.")
        else:
            if process.returncode in [-9, 137]:
                 result_queue.put({'status': 'error', 'data': 'Processo cancelado pelo usuário.'})
            else:
                error_msg = stderr.strip() if stderr and stderr.strip() else "Não foi possível processar a imagem."
                raise Exception(error_msg)
    except subprocess.TimeoutExpired:
        result_queue.put({'status': 'error', 'data': 'O processo de conversão demorou mais de 5 minutos (timeout).'})
    except Exception as e:
        result_queue.put({'status': 'error', 'data': str(e)})


# ... (As rotas / e /process continuam as mesmas) ...
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_upload():
    if 'image' not in request.files or not request.files['image'].filename:
        return "Nenhum arquivo enviado", 400
    file = request.files['image']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    task_id = str(uuid.uuid4())
    return redirect(url_for('processing_page', filename=filename, task_id=task_id))

@app.route('/processing/<filename>/<task_id>')
def processing_page(filename, task_id):
    return render_template('processing.html', filename=filename, task_id=task_id)


@app.route('/stream-process/<filename>/<task_id>')
def stream_process(filename, task_id):
    def generate():
        # ... (A lógica inicial da função 'generate' continua a mesma) ...
        result_queue = queue.Queue()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        container_name = f"osra-task-{task_id}"
        docker_cmd = [
            "docker", "run", "--rm", f"--name={container_name}",
            "-v", f"{os.path.dirname(os.path.abspath(file_path))}:/data",
            "daverona/osra", "osra", "-f", "smi", f"/data/{os.path.basename(file_path)}"
        ]
        with PROCESS_LOCK:
            ACTIVE_TASKS.add(task_id)
        thread = threading.Thread(target=run_osra_in_thread, args=(docker_cmd, result_queue))
        thread.start()
        
        try:
            yield "data: Processo iniciado...\n\n"
            while thread.is_alive():
                with PROCESS_LOCK:
                    if task_id not in ACTIVE_TASKS:
                        break
                yield "data: :heartbeat\n\n"
                time.sleep(2)
            
            result = result_queue.get_nowait()
            
            if result['status'] == 'success':
                smiles = result['data']
                mol = Chem.MolFromSmiles(smiles)
                
                # --- MODIFICADO: Payload final agora inclui os dados 3D ---
                final_payload = {
                    "status": "success",
                    "smiles": smiles,
                    "inchi": Chem.MolToInchi(mol),
                    "inchikey": Chem.InchiToInchiKey(Chem.MolToInchi(mol)),
                    "molecule_svg": generate_molecule_svg(mol),
                    "contains_r_group": result['contains_r_group'],
                    "mol_weight": f"{Descriptors.MolWt(mol):.3f}",
                    "mol_formula": CalcMolFormula(mol),
                    "logp": f"{Descriptors.MolLogP(mol):.3f}",
                    "h_donors": Descriptors.NumHDonors(mol),
                    "h_acceptors": Descriptors.NumHAcceptors(mol),
                    "tpsa": f"{Descriptors.TPSA(mol):.2f}",
                    "molecule_sdf": generate_3d_sdf(mol) # Adiciona os dados 3D
                }
                # --------------------------------------------------------

                yield f"data: {json.dumps(final_payload)}\n\n"
            else:
                raise Exception(result['data'])

        except queue.Empty:
            yield f"data: {json.dumps({'status': 'error', 'message': 'A tarefa foi cancelada antes da conclusão.'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        finally:
            with PROCESS_LOCK:
                ACTIVE_TASKS.discard(task_id)

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


# ... (A rota /cancel e o if __name__ == '__main__' continuam os mesmos) ...
@app.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    with PROCESS_LOCK:
        if task_id in ACTIVE_TASKS:
            container_name = f"osra-task-{task_id}"
            try:
                subprocess.run(['docker', 'stop', container_name], check=True, capture_output=True, timeout=10)
            except Exception:
                pass 
            finally:
                ACTIVE_TASKS.discard(task_id)
                return jsonify({'status': 'success', 'message': 'Sinal de cancelamento processado.'})
    return jsonify({'status': 'not_found', 'message': 'Tarefa não encontrada ou já concluída.'})


if __name__ == '__main__':
    from waitress import serve
    print("Servidor Waitress rodando em http://0.0.0.0:8080")
    print("Acesse http://127.0.0.1:8080 no seu navegador.")
    serve(app, host='0.0.0.0', port=8080)
