import streamlit as st
import fitz  # PyMuPDF
import os
import json

PROGRESS_FILE = "read_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_progress():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "volume": st.session_state.current_volume, 
            "chunk": st.session_state.current_chunk,
            "zoom": st.session_state.get("zoom_width", 700),
            "saved_page": st.session_state.get("saved_page")
        }, f)

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
    # --- БОКОВОЕ МЕНЮ (НАВИГАЦИЯ) ---
    st.sidebar.header("Навигация")

    # Инициализация переменной для запоминания тома из файла
    saved_data = load_progress()

    if 'current_volume' not in st.session_state:
        st.session_state.current_volume = saved_data.get("volume", pdf_files[0] if pdf_files else None)
        st.session_state.do_bookmark_scroll = True # Флаг для скролла при первом заходе
    if 'current_chunk' not in st.session_state:
        st.session_state.current_chunk = saved_data.get("chunk", 1)
    if 'saved_page' not in st.session_state:
        st.session_state.saved_page = saved_data.get("saved_page")

    # Защита от случая, если сохраненный том был удален
    if st.session_state.current_volume not in pdf_files and pdf_files:
        st.session_state.current_volume = pdf_files[0]
        st.session_state.current_chunk = 1

    # Находим индекс последнего прочитанного тома (для selectbox)
    try:
        default_index = pdf_files.index(st.session_state.current_volume)
    except ValueError:
        default_index = 0

    # Выбор PDF-файла (выбранный том обновляет сессию)
    selected_pdf = st.sidebar.selectbox("Выберите том:", pdf_files, index=default_index)
    pdf_path = os.path.join(MANGA_FOLDER, selected_pdf)

    # Если пользователь вручную сменил том — сбрасываем прогресс чтения на 1-ю часть
    if st.session_state.current_volume != selected_pdf:
        st.session_state.current_volume = selected_pdf
        st.session_state.current_chunk = 1
        st.session_state.saved_page = None
        st.session_state.scroll_to_top = True
        save_progress()

    # Используем with для безопасного открытия файла, чтобы узнать количество страниц
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)

    st.sidebar.write(f"📖 Всего страниц в томе: {total_pages}")

    st.sidebar.markdown("---")
    st.sidebar.header("Настройки")
    
    # Callback для сохранения зума при движении ползунка
    def on_zoom_change():
        save_progress()

    saved_zoom = saved_data.get("zoom", 700)
    zoom_width = st.sidebar.slider(
        "🔍 Масштаб (ширина)", 
        min_value=300, max_value=2000, value=saved_zoom, step=100, 
        key="zoom_width",
        on_change=on_zoom_change,
        help="Увеличьте ползунок, чтобы растянуть мангу на весь экран ПК"
    )
    
    # Внедряем CSS-стиль для переопределения стандартной узкой ширины Streamlit
    st.markdown(f"<style>.block-container {{ max-width: {zoom_width}px !important; padding-top: 2rem; }}</style>", unsafe_allow_html=True)

    # Считаем общее количество частей (округление вверх)
    total_chapters = (total_pages + PAGES_PER_CHAPTER - 1) // PAGES_PER_CHAPTER

    # Вспомогательные функции для переключения по кнопкам
    def update_and_save(new_chunk):
        st.session_state.current_chunk = new_chunk
        st.session_state.saved_page = None # Сбрасываем закладку при ручном перелистывании
        st.session_state.scroll_to_top = True
        save_progress()

    def set_bookmark(page_idx):
        st.session_state.saved_page = page_idx
        save_progress()

    def go_first():
        update_and_save(1)

    def go_prev():
        if st.session_state.current_chunk > 1:
            update_and_save(st.session_state.current_chunk - 1)

    def go_next():
        if st.session_state.current_chunk < total_chapters:
            update_and_save(st.session_state.current_chunk + 1)

    def go_last():
        update_and_save(total_chapters)

    # Прокрутка страницы наверх после смены части
    if st.session_state.get("scroll_to_top", False):
        js = '''
        <script>
            var body = window.parent.document.querySelector(".main");
            if (body) body.scrollTop = 0;
            window.parent.scrollTo(0,0);
        </script>
        '''
        import streamlit.components.v1 as components
        components.html(js, height=0)
        st.session_state.scroll_to_top = False
    elif st.session_state.get("do_bookmark_scroll", False) and st.session_state.get("saved_page") is not None:
        p = st.session_state.saved_page
        js = f'''
        <script>
            setTimeout(function() {{
                var target = window.parent.document.getElementById("manga_page_{p}");
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "start"}});
                }}
            }}, 800);
        </script>
        '''
        import streamlit.components.v1 as components
        components.html(js, height=0)
        st.session_state.do_bookmark_scroll = False

    # --- ВЕРХНИЙ БЛОК НАВИГАЦИИ (До страниц) ---
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 3, 1.5, 1.5])
    
    # Красивое название тома без .pdf и подчеркиваний
    display_volume = selected_pdf.replace(".pdf", "").replace("_", " ")

    with col1:
        st.button("⏮️ В начало", on_click=go_first, disabled=(st.session_state.current_chunk == 1), key="first_top", use_container_width=True)
    with col2:
        st.button("⬅️ Назад", on_click=go_prev, disabled=(st.session_state.current_chunk == 1), key="prev_top", use_container_width=True)
    with col3:
        st.markdown(f"<div style='text-align: center; margin-top: -5px; font-weight: bold; color: #ff4b4b;'>📖 {display_volume}</div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; margin-top: 0;'>Часть {st.session_state.current_chunk} из {total_chapters}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; margin-top: -10px; color: gray;'>Стр. {((st.session_state.current_chunk - 1) * PAGES_PER_CHAPTER) + 1} - {min(st.session_state.current_chunk * PAGES_PER_CHAPTER, total_pages)}</p>", unsafe_allow_html=True)
    with col4:
        st.button("Вперед ➡️", on_click=go_next, disabled=(st.session_state.current_chunk == total_chapters), key="next_top", use_container_width=True)
    with col5:
        st.button("В конец ⏭️", on_click=go_last, disabled=(st.session_state.current_chunk == total_chapters), key="last_top", use_container_width=True)
    st.markdown("---")

    # Вычисляем страницы для рендера
    chapter = st.session_state.current_chunk
    start_page = (chapter - 1) * PAGES_PER_CHAPTER
    end_page = min(start_page + PAGES_PER_CHAPTER, total_pages)

    # Рендерим загруженные 20 страниц
    for page_num in range(start_page, end_page):
        # Якорь для скролла
        st.markdown(f'<div id="manga_page_{page_num}"></div>', unsafe_allow_html=True)
        
        # Достаем картинку из нашего кэша
        img_bytes = get_pdf_page_image(pdf_path, page_num)
        st.image(img_bytes, use_container_width=True)
        
        # Кнопка для сохранения точной позиции (закладка)
        cf1, cf2, cf3 = st.columns([1, 1.5, 1])
        with cf2:
            is_saved = (st.session_state.get("saved_page") == page_num)
            btn_text = f"✅ Вы остановились здесь (Стр. {page_num + 1})" if is_saved else f"📍 Запомнить это место (Стр. {page_num + 1})"
            
            # Используем on_click (Callback), чтобы избежать жесткого rerun и зависаний
            st.button(
                btn_text, 
                key=f"bm_{page_num}", 
                use_container_width=True, 
                disabled=is_saved, 
                on_click=set_bookmark, 
                args=(page_num,)
            )
                
        st.markdown("---")

    # --- НИЖНИЙ БЛОК НАВИГАЦИИ (После страниц) ---
    col1_b, col2_b, col3_b, col4_b, col5_b = st.columns([1.5, 1.5, 3, 1.5, 1.5])
    with col1_b:
        st.button("⏮️ В начало", on_click=go_first, disabled=(st.session_state.current_chunk == 1), key="first_bottom", use_container_width=True)
    with col2_b:
        st.button("⬅️ Назад", on_click=go_prev, disabled=(st.session_state.current_chunk == 1), key="prev_bottom", use_container_width=True)
    with col3_b:
        st.markdown(f"<h4 style='text-align: center; margin-top: 0;'>Вверх или дальше?</h4>", unsafe_allow_html=True)
    with col4_b:
        st.button("Вперед ➡️", on_click=go_next, disabled=(st.session_state.current_chunk == total_chapters), key="next_bottom", use_container_width=True)
    with col5_b:
        st.button("В конец ⏭️", on_click=go_last, disabled=(st.session_state.current_chunk == total_chapters), key="last_bottom", use_container_width=True)
    st.markdown("---")
