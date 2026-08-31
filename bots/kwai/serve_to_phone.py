import os
import csv
import socket
import http.server
import socketserver
import shutil

# Configurações
CSV_PATH = "data/cronograma_kwai.csv"
SERVE_DIR = "web_export"
PORT = 8080

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # não precisa estar alcançável, só para pegar o IP da interface padrão
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def generate_html():
    # Sobe um diretório se estivermos em bots/kwai
    base_dir = os.getcwd()
    if os.path.basename(base_dir) == 'kwai':
        base_dir = os.path.dirname(os.path.dirname(base_dir))
    
    csv_full = os.path.join(base_dir, CSV_PATH)
    serve_full = os.path.join(base_dir, SERVE_DIR)

    if os.path.exists(serve_full):
        shutil.rmtree(serve_full)
    os.makedirs(serve_full)

    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exportação Kwai - O Estoico Moderno</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; color: #333; }
            h1 { text-align: center; color: #ff5000; }
            .card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            video { width: 100%; max-height: 400px; border-radius: 8px; background: #000; }
            .caption { background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #eee; margin-top: 15px; white-space: pre-wrap; font-size: 14px; }
            .copy-btn { background: #ff5000; color: #fff; border: none; padding: 10px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; }
            .download-btn { display: block; text-align: center; background: #25D366; color: #fff; text-decoration: none; padding: 12px; border-radius: 6px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Postagens Kwai 🚀</h1>
    """

    import zipfile
    zip_path = os.path.join(serve_full, "todos_os_videos.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        with open(csv_full, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                video_path = row['caminho_midia']
                video_name = os.path.basename(video_path)
                full_text = row['texto']
                data_post = f"{row['data']} às {row['hora']}"
                
                # Copiar o video para a pasta web
                dest_video = os.path.join(serve_full, f"video_{i}.mp4")
                shutil.copy2(video_path, dest_video)
                # Adicionar ao zip
                zipf.write(dest_video, arcname=f"video_{i}.mp4")

                html_content += f"""
                <div class="card">
                    <h3>Post {i+1} - {data_post}</h3>
                    <div class="caption" id="cap{i}">{full_text}</div>
                    <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('cap{i}').innerText); alert('Legenda copiada!');">📋 Copiar Legenda + Hashtags</button>
                </div>
                """

    html_content = html_content.replace(
        "<h1>Postagens Kwai 🚀</h1>", 
        "<h1>Postagens Kwai 🚀</h1>\n<a href='todos_os_videos.zip' download='todos_os_videos.zip' style='display:block; background:#007aff; color:#fff; text-align:center; padding:15px; border-radius:8px; font-weight:bold; text-decoration:none; margin-bottom:20px; font-size:18px;'>📦 BAIXAR TODOS OS VÍDEOS (ZIP)</a>"
    )

    html_content += """
    </body>
    </html>
    """

    with open(os.path.join(serve_full, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    return serve_full

if __name__ == "__main__":
    print("Gerando painel para o seu iPhone...")
    serve_dir = generate_html()
    ip = get_local_ip()
    
    os.chdir(serve_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    print("\n" + "="*50)
    print("✅ TUDO PRONTO! ✅")
    print(f"Pegue o seu iPhone, abra o Safari e digite exatamente isso:")
    print(f"👉  http://{ip}:{PORT}  👈")
    print("="*50 + "\n")
    print("Pressione Ctrl+C no terminal para desligar quando terminar de baixar tudo.")
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor desligado.")
