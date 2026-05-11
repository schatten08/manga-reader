import streamlit as st
import fitz  # PyMuPDF
import os

# --- Кэширование функции рендера для ускорения интерфейса ---
@st.cache_data(show_spinner=False)
def get_pdf_page_image(pdf_path, page_num):
    # Открываем и сразу закрываем документ для одной страницы (зато кэшируется результат байтов)
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_num)
        zoom_matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=zoom_matrix)
        return pix.tobytes("png")

st.set_page_config(page_title="Manga Reader", layout="centered")
st.title("🏴‍☠️ Manga Reader (One Piece)")

MANGA_FOLDER = r"C:\Users\andrei_trokol\OneDrive - EPAM\OnePiece"
PAGES_PER_CHAPTER = 20

if not os.path.exists(MANGA_FOLDER):
    os.makedirs(MANGA_FOLDER)

pdf_files = [f for f in os.listdir(MANGA_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    st.warning(f"⚠️ Папка `{MANGA_FOLDER}` пуста.")
    st.info("💡 Инструкция:\n1. Закиньте любой PDF файл (том манги) в папку `manga_files`.\n2. Обновите страницу.")
else:
    st.sidebar.header("Навигация")

    # Выбор PDF-файла
    selected_pdf = st.sidebar.selectbox("Выберите том:", pdf_files)
    pdf_path = os.path.join(MANGA_FOLDER, selected_pdf)

    # Используем with для безопасного открытия файла, чтобы узнать количество страниц
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

    st.sidebar.write(f"📖 Всего страниц в томе: {total_pages}")

    total_chapters = (total_pages // PAGES_PER_CHAPTER) + 1

    # Сохраняем логику разбивки
    chapter = st.sidebar.slider("Часть (глава):", 1, total_chapters, 1)

    start_page = (chapter - 1) * PAGES_PER_CHAPTER
    end_page = min(start_page + PAGES_PER_CHAPTER, total_pages)

    st.write(f"### Читаем страницы: {start_page + 1} - {end_page}")

    # Рендерим страницы
    for page_num in range(start_page, end_page):
        # Если страница уже запрашивалась ранее, Streamlit возьмет её мгновенно из кэша ORAM
        img_bytes = get_pdf_page_image(pdf_path, page_num)
        
        st.image(img_bytes, use_container_width=True)
        st.markdown("---")
