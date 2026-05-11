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

    # Если сменили том — сбрасываем прогресс чтения на 1-ю часть
    if 'current_volume' not in st.session_state or st.session_state.current_volume != selected_pdf:
        st.session_state.current_volume = selected_pdf
        st.session_state.current_chunk = 1

    # Используем with для безопасного открытия файла, чтобы узнать количество страниц
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

    st.sidebar.write(f"📖 Всего страниц в томе: {total_pages}")

    # Считаем общее количество частей (округление вверх)
    total_chapters = (total_pages + PAGES_PER_CHAPTER - 1) // PAGES_PER_CHAPTER

    # Вспомогательные функции для переключения по кнопкам
    def go_prev():
        if st.session_state.current_chunk > 1:
            st.session_state.current_chunk -= 1

    def go_next():
        if st.session_state.current_chunk < total_chapters:
            st.session_state.current_chunk += 1

    # --- ВЕРХНИЙ БЛОК НАВИГАЦИИ (До страниц) ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("⬅️ Назад", on_click=go_prev, disabled=(st.session_state.current_chunk == 1), key="prev_top", use_container_width=True)
    with col2:
        st.markdown(f"<h4 style='text-align: center; margin-top: 0;'>Часть {st.session_state.current_chunk} из {total_chapters}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; margin-top: -10px; color: gray;'>Стр. {((st.session_state.current_chunk - 1) * PAGES_PER_CHAPTER) + 1} - {min(st.session_state.current_chunk * PAGES_PER_CHAPTER, total_pages)}</p>", unsafe_allow_html=True)
    with col3:
        st.button("Вперед ➡️", on_click=go_next, disabled=(st.session_state.current_chunk == total_chapters), key="next_top", use_container_width=True)
    st.markdown("---")

    # Вычисляем страницы для рендера
    chapter = st.session_state.current_chunk
    start_page = (chapter - 1) * PAGES_PER_CHAPTER
    end_page = min(start_page + PAGES_PER_CHAPTER, total_pages)

    # Рендерим загруженные 20 страниц
    for page_num in range(start_page, end_page):
        # Достаем картинку из нашего кэша
        img_bytes = get_pdf_page_image(pdf_path, page_num)
        st.image(img_bytes, use_container_width=True)
        st.markdown("---")

    # --- НИЖНИЙ БЛОК НАВИГАЦИИ (После страниц) ---
    col1_b, col2_b, col3_b = st.columns([1, 2, 1])
    with col1_b:
        st.button("⬅️ Назад", on_click=go_prev, disabled=(st.session_state.current_chunk == 1), key="prev_bottom", use_container_width=True)
    with col2_b:
        st.markdown(f"<h4 style='text-align: center; margin-top: 0;'>Вверх или дальше?</h4>", unsafe_allow_html=True)
    with col3_b:
        st.button("Вперед ➡️", on_click=go_next, disabled=(st.session_state.current_chunk == total_chapters), key="next_bottom", use_container_width=True)
    st.markdown("---")
