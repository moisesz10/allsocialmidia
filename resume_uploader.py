"""
Resume Uploader v4 - Corrige:
  - Handler de JS dialog (Leave page? / beforeunload)
  - keyboard.type() com delay (mais confiável que execCommand via CDP)
  - wait_for_selector explícito para SCHEDULE button
  - Página única reutilizada (como original que funcionou)
"""
import csv
import sys
import time
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

CHANNEL_ID = "UCTF5YuHGPHAk5qX503vEiPV"
UPLOAD_URL = f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/upload?d=ud"


def upload_video(page, video_path: str, title: str, description: str,
                 schedule_date: str, schedule_time: str) -> bool:
    print(f"\n🎬 Upload: {title[:65]}")
    print(f"   📅 {schedule_date} às {schedule_time}")

    # Navegar para upload (networkidle como original)
    page.goto(UPLOAD_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Enviar arquivo
    print(f"   📁 {os.path.basename(video_path)}")
    try:
        page.locator("input[type=file]").set_input_files(video_path, timeout=20000)
    except Exception as e:
        print(f"   ❌ Erro no arquivo: {e}")
        return False

    # Aguardar upload completo — espera o botão Next habilitar
    print("   ⏳ Aguardando upload processar...")
    try:
        page.wait_for_selector(
            "ytcp-button#next-button:not([disabled])",
            timeout=120000
        )
        print("   ✅ Upload OK, Next habilitado!")
    except Exception:
        print("   ⚠️  Timeout aguardando Next, continuando...")
    time.sleep(2)

    # ── Preencher Título ────────────────────────────────────────
    print("   ✏️  Título...")
    try:
        title_box = page.locator("div#textbox").first
        title_box.click(force=True, timeout=10000)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(title, delay=30)
        time.sleep(0.5)
        # Trigger input event para YouTube reconhecer
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#textbox')[0];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
    except Exception as e:
        print(f"   ⚠️  Título: {e}")

    # ── Preencher Descrição ────────────────────────────────────
    print("   ✏️  Descrição...")
    try:
        desc_box = page.locator("div#textbox").nth(1)
        desc_box.click(force=True, timeout=10000)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.keyboard.type(description, delay=10)
        time.sleep(0.5)
        page.evaluate("""() => {
            const b = document.querySelectorAll('div#textbox')[1];
            if (b) b.dispatchEvent(new InputEvent('input', {bubbles:true}));
        }""")
    except Exception as e:
        print(f"   ⚠️  Descrição: {e}")

    # ── Não é para crianças ────────────────────────────────────
    try:
        page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click(
            force=True, timeout=5000
        )
        time.sleep(1)
    except Exception:
        pass

    # ── Avançar step a step até Visibility ─────────────────────
    print("   ➡️  Avançando para Visibility...")
    for attempt in range(10):  # até 10 tentativas
        # Checar se SCHEDULE já apareceu
        try:
            sched = page.locator("tp-yt-paper-radio-button[name='SCHEDULE']")
            if sched.is_visible(timeout=1000):
                print("   ✅ Aba Visibility encontrada!")
                break
        except Exception:
            pass

        # Clicar Next se disponível
        try:
            next_btn = page.locator("ytcp-button#next-button")
            if next_btn.is_visible(timeout=1000) and next_btn.is_enabled(timeout=1000):
                next_btn.click(force=True)
                time.sleep(3)
        except Exception:
            pass
    else:
        print("   ❌ Não chegou na aba Visibility após 10 tentativas.")
        return False

    # ── Configurar Agendamento ─────────────────────────────────
    print(f"   🗓️  Agendando {schedule_date} às {schedule_time}...")
    try:
        page.locator("tp-yt-paper-radio-button[name='SCHEDULE']").click(force=True)
        time.sleep(1)

        # Data
        page.locator("ytcp-text-dropdown-trigger#datepicker-trigger").click(force=True)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(schedule_date)
        page.keyboard.press("Enter")
        time.sleep(1)

        # Horário
        page.locator("ytcp-text-dropdown-trigger#time-of-day-trigger").click(force=True)
        time.sleep(0.5)
        page.keyboard.press("Control+A")
        page.keyboard.insert_text(schedule_time)
        page.keyboard.press("Enter")
        time.sleep(1)
    except Exception as e:
        print(f"   ❌ Erro no agendamento: {e}")
        return False

    # ── Confirmar ───────────────────────────────────────────────
    print("   ✅ Confirmando...")
    try:
        done_btn = page.locator("ytcp-button#done-button")
        done_btn.wait_for(state="visible", timeout=15000)
        done_btn.click(force=True)
        time.sleep(5)
        try:
            page.locator("ytcp-button#close-button").click(force=True, timeout=5000)
        except Exception:
            pass
        print("   🎉 Agendado com sucesso!")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao confirmar: {e}")
        return False


def run_resume(csv_path: str):
    print("=" * 62)
    print("🤖 RESUME UPLOADER v4")
    print("=" * 62)

    videos: dict = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            videos[row["video_id"]] = row

    start_date = datetime(2026, 8, 24)
    pairs = []
    for i in range(1, 6):
        d = (start_date + timedelta(days=i - 1)).strftime("%d/%m/%Y")
        pairs.append({
            "n":     i,
            "date":  d,
            "short": videos.get(f"video_0{i}_short"),
            "long":  videos.get(f"video_0{i}_long"),
        })

    print("\n📌 Agenda:")
    for p in pairs:
        if p["short"]:
            print(f"  Par {p['n']} | {p['date']} | SHORT 11:30 | {p['short']['titulo'][:55]}")
        if p["n"] == 5 and p["long"]:
            print(f"  Par {p['n']} | {p['date']} | LONG  19:00 | {p['long']['titulo'][:55]}")
    print()

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("http://localhost:9222")
        print("✅ Conectado!\n")
        context = browser.contexts[0]
        page = context.new_page()

        # ── Handler de JS dialogs (Leave page? etc.) ────────────
        page.on("dialog", lambda d: (print(f"   💬 Dialog auto-dismiss: {d.message[:60]}"), d.accept()))

        ok_count = fail_count = 0

        for p in pairs:
            # SHORT
            if p["short"]:
                s = p["short"]
                path = os.path.abspath(s["caminho_arquivo_video"])
                if not os.path.exists(path):
                    print(f"⚠️  Arquivo não encontrado: {path}")
                    fail_count += 1
                else:
                    desc = s["legenda_post"] + "\n\n" + s["hashtags"]
                    ok = upload_video(page, path, s["titulo"], desc, p["date"], "11:30")
                    ok_count += ok; fail_count += not ok
                    time.sleep(8)

            # LONG (só par 5)
            if p["n"] == 5 and p["long"]:
                l = p["long"]
                path = os.path.abspath(l["caminho_arquivo_video"])
                if not os.path.exists(path):
                    print(f"⚠️  Arquivo não encontrado: {path}")
                    fail_count += 1
                else:
                    desc = l["legenda_post"] + "\n\n" + l["hashtags"]
                    ok = upload_video(page, path, l["titulo"], desc, p["date"], "19:00")
                    ok_count += ok; fail_count += not ok
                    time.sleep(8)

        print("\n" + "=" * 62)
        print(f"🏁 Concluído! ✅ Sucesso: {ok_count}  ❌ Falhas: {fail_count}")
        print("=" * 62)
        page.close()


if __name__ == "__main__":
    csv_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "output/batch_20260822_212315/cronograma_publicacoes.csv"
    )
    run_resume(csv_path)
