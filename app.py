import streamlit as st
import anthropic
import base64
import os
import io
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="Садовый помощник",
    page_icon="🌿",
    layout="centered"
)

# ── STYLES ────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@keyframes fadeIn  { from{opacity:0;transform:translateY(-10px)} to{opacity:1;transform:translateY(0)} }
@keyframes slideUp { from{opacity:0;transform:translateY(28px)}  to{opacity:1;transform:translateY(0)} }

* { font-family:'Inter',sans-serif !important; }

.stApp { background-color:#dff5f0 !important; }
#MainMenu,footer,header { visibility:hidden; }

/* Hero */
.hero { text-align:center; padding:0 0 1rem; animation:fadeIn .7s ease; }
.hero-title {
    font-size:2.5rem; font-weight:700; color:#0d9488;
    text-shadow:0 2px 24px rgba(13,148,136,.18); margin-bottom:.35rem;
}
.hero-sub { font-size:.88rem; color:#0f766e; letter-spacing:.06em; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,.35) !important;
    border:1px solid rgba(13,148,136,.18) !important;
    border-radius:14px !important; padding:6px !important; gap:8px !important;
}
.stTabs [data-baseweb="tab"] {
    background:rgba(255,255,255,.45) !important; color:#0f766e !important;
    border-radius:10px !important; font-weight:500 !important; font-size:.88rem !important;
    padding:.5rem 1.1rem !important; transition:all .22s ease !important;
    border:1px solid rgba(13,148,136,.2) !important; letter-spacing:.04em !important;
    flex:1 !important; text-align:center !important;
    box-shadow:0 2px 8px rgba(0,0,0,.06) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color:#0d9488 !important; background:rgba(255,255,255,.92) !important;
    border-color:rgba(13,148,136,.42) !important;
    transform:translateY(-1px) !important;
    box-shadow:0 5px 16px rgba(13,148,136,.12) !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(145deg,rgba(13,148,136,.22) 0%,rgba(20,184,166,.12) 55%,rgba(13,148,136,.08) 100%) !important;
    color:#0d9488 !important;
    border:1px solid rgba(13,148,136,.5) !important;
    box-shadow:0 3px 18px rgba(13,148,136,.15), inset 0 1px 0 rgba(255,255,255,.4) !important;
    transform:translateY(0) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }

/* Buttons */
.stButton>button {
    background:linear-gradient(135deg,#0d9488,#0f766e) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:600 !important; padding:.55rem 1.6rem !important;
    transition:all .25s ease !important; box-shadow:0 4px 18px rgba(13,148,136,.25) !important;
}
.stButton>button:hover  { transform:translateY(-2px) !important; box-shadow:0 8px 28px rgba(13,148,136,.38) !important; }
.stButton>button:active { transform:translateY(0) !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background:rgba(255,255,255,.65) !important;
    border:2px dashed rgba(13,148,136,.28) !important; border-radius:12px !important;
    transition:all .3s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color:rgba(13,148,136,.6) !important; background:rgba(255,255,255,.88) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > span { font-size:0 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > span::before {
    content:"Перетащи фото сюда"; font-size:.9rem; color:#0f766e;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div > small { font-size:0 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > small::before {
    content:"JPG, PNG, WEBP"; font-size:.78rem; color:#0d948866;
}
[data-testid="stFileUploaderDropzone"] button { font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] button::before { content:"Выбрать файл"; font-size:.85rem; color:#0f766e; }

/* Camera input */
[data-testid="stCameraInput"] > div {
    border-radius:12px !important; border:1px solid rgba(13,148,136,.2) !important;
    overflow:hidden !important; background:rgba(255,255,255,.5) !important;
}
[data-testid="stCameraInput"] video, [data-testid="stCameraInput"] img { border-radius:10px !important; }
[data-testid="stCameraInputButton"] {
    background:linear-gradient(135deg,#0d9488,#0f766e) !important;
    border:none !important; border-radius:10px !important;
    color:#fff !important; font-weight:600 !important;
    box-shadow:0 4px 18px rgba(13,148,136,.2) !important;
    font-size:0 !important;
}
[data-testid="stCameraInputButton"]::before {
    content:"Сфотографировать"; font-size:1rem; font-weight:600;
}
.camera-divider { text-align:center; color:#0d948866; font-size:.8rem; padding:.5rem 0; letter-spacing:.06em; }

/* Text input */
[data-testid="stTextInputRootElement"],
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background:rgba(255,255,255,.78) !important;
    border-color:rgba(13,148,136,.22) !important; border-radius:10px !important;
}
[data-testid="stTextInputRootElement"] input,
.stTextInput input {
    background:transparent !important;
    color:#134e4a !important; -webkit-text-fill-color:#134e4a !important; caret-color:#0d9488 !important;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-baseweb="input"]:focus-within {
    border-color:rgba(13,148,136,.55) !important;
    box-shadow:0 0 18px rgba(13,148,136,.1) !important; outline:none !important;
}
.stTextInput input::placeholder { color:#0d948866 !important; }

/* Textarea */
textarea {
    background:rgba(255,255,255,.78) !important;
    border-color:rgba(13,148,136,.22) !important; border-radius:10px !important;
    color:#134e4a !important; -webkit-text-fill-color:#134e4a !important; caret-color:#0d9488 !important;
}
textarea::placeholder { color:#0d948866 !important; }

/* Selectbox */
[data-testid="stSelectbox"]>div>div {
    background:rgba(255,255,255,.78) !important;
    border:1px solid rgba(13,148,136,.22) !important; border-radius:10px !important;
    color:#134e4a !important; transition:all .25s ease !important;
}

/* Chat input */
[data-testid="stChatInputTextArea"] {
    background:rgba(255,255,255,.72) !important;
    border:1px solid rgba(13,148,136,.22) !important; border-radius:12px !important;
    color:#134e4a !important; -webkit-text-fill-color:#134e4a !important; caret-color:#0d9488 !important;
    transition:all .25s ease !important;
}
[data-testid="stChatInputTextArea"]:focus {
    border-color:rgba(13,148,136,.5) !important; box-shadow:0 0 18px rgba(13,148,136,.08) !important;
}
[data-testid="stChatInputTextArea"]::placeholder { color:#0d948855 !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background:rgba(255,255,255,.42) !important;
    border:1px solid rgba(13,148,136,.1) !important; border-radius:14px !important;
    padding:1rem !important; margin:5px 0 !important; animation:slideUp .35s ease;
}

/* Text colors */
.stMarkdown,.stMarkdown p,.stMarkdown li,.stMarkdown td,.stMarkdown th { color:#134e4a !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 { color:#0d9488 !important; font-weight:600 !important; }
h2,h3 { color:#0d9488 !important; font-weight:600 !important; }
label,.stCheckbox label { color:#0f766e !important; }
p { color:#134e4a !important; }
hr { border-color:rgba(13,148,136,.15) !important; }
.stCaption { color:#0f766e !important; }

/* Expander */
[data-testid="stExpander"] details summary {
    background:rgba(255,255,255,.38) !important;
    border:1px solid rgba(13,148,136,.18) !important; border-radius:10px !important;
    color:#0d9488 !important; transition:all .25s ease !important; padding:.7rem 1rem !important;
}
[data-testid="stExpander"] details summary:hover { background:rgba(255,255,255,.6) !important; }
[data-testid="stExpander"] details[open] summary { border-radius:10px 10px 0 0 !important; }

/* Divider */
[data-testid="stDivider"] { border-color:rgba(13,148,136,.15) !important; }

/* Spinner */
[data-testid="stSpinner"]>div { border-top-color:#0d9488 !important; }

/* Image */
[data-testid="stImage"] img {
    border-radius:12px !important; border:1px solid rgba(13,148,136,.18) !important;
}

/* Toggle */
[data-testid="stToggle"] label { color:#0f766e !important; }

/* Custom components */
.result-card {
    background:rgba(255,255,255,.45); border:1px solid rgba(13,148,136,.18);
    border-radius:14px; padding:1.4rem 1.6rem; margin-top:.8rem;
    animation:slideUp .5s ease;
}
.result-label {
    font-size:.78rem; text-transform:uppercase; letter-spacing:.1em;
    color:#0f766e; margin-bottom:.6rem;
}

.task-item {
    background:rgba(255,255,255,.38); border:1px solid rgba(13,148,136,.12);
    border-radius:10px; padding:.7rem 1rem; margin:.32rem 0;
    color:#134e4a; font-size:.92rem; line-height:1.45;
    transition:all .22s ease; display:flex; align-items:flex-start; gap:.55rem;
}
.task-item:hover {
    background:rgba(255,255,255,.88); border-color:rgba(13,148,136,.3);
    transform:translateX(5px);
}
.task-dot { color:#0d9488; font-size:1.1rem; line-height:1.3; flex-shrink:0; }

.task-item.has-details { display:block; padding:0; }
.task-item.has-details details { width:100%; }
.task-item.has-details details summary {
    display:flex; align-items:flex-start; gap:.55rem;
    padding:.7rem 1rem; cursor:pointer; list-style:none;
    color:#134e4a; font-size:.92rem; line-height:1.45;
}
.task-item.has-details details summary::-webkit-details-marker { display:none; }
.task-item.has-details details summary::marker { display:none; }
.task-dot-arrow {
    color:#0d9488; font-size:.85rem; line-height:1.5; flex-shrink:0;
    transition:transform .2s ease; display:inline-block;
}
details[open] .task-dot-arrow { transform:rotate(90deg); }
.task-details {
    margin:.2rem .7rem .7rem 2.3rem; padding:.55rem .85rem;
    background:rgba(13,148,136,.06); border-left:2px solid rgba(13,148,136,.28);
    border-radius:0 6px 6px 0; font-size:.84rem; color:#0f766e; line-height:1.65;
}

.month-title {
    font-size:1.3rem; font-weight:600; color:#0d9488;
    margin:1rem 0 .7rem; padding-bottom:.4rem;
    border-bottom:1px solid rgba(13,148,136,.2);
}
.tab-hint {
    font-size:.83rem; color:#0f766e; margin-bottom:1.1rem;
    padding:.55rem .9rem; background:rgba(255,255,255,.38);
    border-radius:8px; border-left:3px solid rgba(13,148,136,.38);
}

.action-panel {
    margin-top:.9rem;
    padding:1.1rem 1.2rem 1rem;
    background:rgba(255,255,255,.45);
    border:1px solid rgba(13,148,136,.18);
    border-radius:14px;
    animation:slideUp .35s ease;
}
.action-panel-label {
    font-size:.78rem; color:#0f766e; margin-bottom:.45rem; letter-spacing:.03em;
}

@media (max-width: 768px) {
    .hero { padding:0 0 .7rem; }
    .hero-title { font-size:1.75rem; }
    .hero-sub { font-size:.78rem; letter-spacing:.02em; }
    .stTabs [data-baseweb="tab"] { padding:.4rem .7rem !important; font-size:.8rem !important; }
    .task-item { font-size:.86rem; padding:.6rem .8rem; }
    .task-details { font-size:.8rem; margin-left:1.8rem; }
    .month-title { font-size:1.1rem; }
    .tab-hint { font-size:.78rem; }
    .result-label { font-size:.72rem; }
}
</style>""", unsafe_allow_html=True)

# ── PROMPTS & DATA ────────────────────────────────────────────────────
SYSTEM_PROMPT = """Ты опытный агроном и садовод широкого профиля. Отвечаешь на вопросы по любым растениям: садовым, огородным, комнатным, дикорастущим, декоративным — без ограничений по видам и культурам.

Основной контекст участка хозяйки (Краснодарский край, Абинский район):
Климат: предгорная зона, не субтропики. Лето жаркое и влажное, зима умеренная, морозы до -15...-20 °C в отдельные годы. Весна ранняя, возможны возвратные заморозки в марте–апреле.
На участке: персики, абрикосы, айва, яблони, груши, чудо-вишня, миндаль, черешня, инжир, земляничник, голубика, смородина, ежевика, малина, крыжовник, клубника, виноград, актинидия, кизил, многолетники, однолетники, теплица, грядки.
Если вопрос касается растений с участка — учитывай климат Абинского района. Если вопрос про другое растение или регион — отвечай в общем агрономическом контексте.

Что ты умеешь:
1. Определять любые растения и сорта — по фото или описанию
2. Диагностировать болезни и вредителей — на любых культурах
3. Составлять план работ — на месяц или другой период
4. Отвечать на вопросы по уходу, подкормкам, посадкам, обрезке

Правила ответов:
- Отвечай по-русски, конкретно и практично
- Если не уверен — скажи об этом прямо, не додумывай
- Препараты указывай те, что доступны в России

Структура ответа зависит от задачи:
- Определение растения/сорта: название → ботанические признаки → особенности сорта → уход
- Диагностика болезни/вредителя: диагноз → причина → схема лечения с препаратами → профилактика
- План работ: по неделям или декадам, с учётом сезона и климата
- Вопрос по уходу: прямой ответ → обоснование → практические сроки"""

def T(task, details=None):
    return {"task": task, "details": details}

CALENDAR = {
    "Январь": [
        T("Проверка хранения луковиц и корневищ"),
        T("Осмотр деревьев на наличие вредителей в коре"),
        T("Обрезка миндаля в конце месяца при тёплой погоде"),
        T("Планирование посевного сезона, заказ семян"),
        T("Посев сельдерея и лука-порея на рассаду",
          "Самые долгорастущие культуры, сеять в январе. Субстрат: торф + перлит (2:1). Температура прорастания: 18–22 °C. Всходы через 14–21 день. Досвечивать 12–14 часов в сутки."),
        T("Подготовка грунта и ёмкостей для рассады"),
    ],
    "Февраль": [
        T("Обрезка плодовых: персик, абрикос, черешня",
          "Обрезать при температуре выше −5 °C. Срезы диаметром более 2 см замазать садовым варом или пастой РанНет."),
        T("Побелка стволов деревьев",
          "Состав: 2–3 кг извести + 300 г медного купороса + 200 г казеинового клея на 10 л воды. Наносить кистью до высоты 1–1,5 м от земли."),
        T("Первая обработка от грибковых болезней — бордоская жидкость 3%",
          "Готовая смесь 3% или: 300 г медного купороса + 400 г негашёной извести на 10 л воды. Расход: 2–3 л на дерево, 0,5–1 л на куст. Обрабатывать по спящим почкам."),
        T("Посев на рассаду: петунии, лобелии, виолы",
          "Петуния: поверхностный посев, не засыпать землёй, накрыть плёнкой. Температура прорастания: 22–25 °C. Всходы через 7–14 дней. Лобелия: аналогично, смешать семена с песком для равномерного посева."),
        T("Посев перца и баклажанов на рассаду (конец февраля)",
          "Перец и баклажан — долгорастущие (70–90 дней до высадки). Температура прорастания: 25–28 °C. Субстрат: универсальный грунт + перлит. После всходов: 20–22 °C днём, 18 °C ночью. Досвечивать при необходимости."),
    ],
    "Март": [
        T("Обработка сада до распускания почек — медный купорос",
          "3%-й раствор: 300 г медного купороса на 10 л воды. Альтернатива: бордоская смесь 3% или железный купорос 5% (500 г на 10 л). Расход: 2–5 л на взрослое дерево."),
        T("Мульчирование клубники",
          "Материалы: солома (слой 5–8 см), агроволокно, опилки хвойных пород (3–5 см). Укладывать вокруг кустов, не засыпая сердечко."),
        T("Подкормка многолетников азотными удобрениями",
          "Мочевина: 20–30 г/м². Аммиачная селитра: 15–20 г/м². Вносить в почву с поливом или в растворе (20 г на 10 л воды)."),
        T("Обрезка малины и ежевики",
          "Малина: вырезать все двухлетние побеги под корень. Ежевика: укоротить однолетние побеги до 1,5 м, вырезать двухлетние."),
        T("Посев томатов на рассаду",
          "Срок: за 55–65 дней до высадки (в Абинском районе — начало–середина марта). Температура прорастания: 23–25 °C. После всходов: 18–20 °C днём, 14–16 °C ночью. Пикировка при появлении 2-го настоящего листа."),
        T("Посев зелени в теплицу: укроп, петрушка, салат, шпинат",
          "Посев рядами, глубина 1–1,5 см. Укроп: 2–3 г/м². Петрушка: 1–2 г/м² (всходит медленно, до 3 недель). Салат: 0,5–1 г/м². Шпинат: 3–4 г/м²."),
        T("Подкормка рассады цветов и овощей",
          "Первая подкормка через 2 недели после пикировки: Кемира Люкс (10 г на 10 л) или Агрикола для рассады (5 мл на 1 л). Повторять каждые 10–14 дней."),
        T("Посадка рассады однолетников дома"),
    ],
    "Апрель": [
        T("Обработка от тли и долгоносика",
          "Тля: Актара (1,4 г на 10 л), Конфидор Экстра (0,5 г на 10 л), Биотлин. Долгоносик: Фуфанон-Нова (10 мл на 10 л), Каратэ Зеон. Обрабатывать в вечернее время."),
        T("Высадка рассады овощей в теплицу (начало апреля)",
          "Томаты: схема 60×50 см, перец 50×40 см, баклажан 60×40 см. После высадки притенить на 3–5 дней, первый полив — через 2–3 дня."),
        T("Посев моркови, свёклы, редиса в открытый грунт",
          "Морковь: 2–4 г/м², глубина 1–2 см. Свёкла: 10–15 г/м², глубина 2–3 см. Редис: 3–5 г/м², глубина 1–1,5 см. Оптимальная температура почвы — от +8 °C."),
        T("Посадка рассады цветов в открытый грунт (с середины апреля)",
          "Высаживать после последних заморозков (в Абинском — ориентировочно 15–20 апреля). Виолы, алиссум, лобелию можно раньше — они холодостойки."),
        T("Подвязка винограда, обломка лишних побегов"),
        T("Подкормка плодовых деревьев азотом",
          "Мочевина: 200–250 г под дерево в приствольный круг с поливом. Или жидко: 30 г мочевины на 10 л — полить по периметру кроны."),
    ],
    "Май": [
        T("Борьба с сорняками, мульчирование приствольных кругов"),
        T("Обработка от монилиоза — персик, черешня, абрикос",
          "Препараты: Хорус (3,5 г на 10 л) — эффективен при прохладной погоде; Скор (2 мл на 10 л); Свитч (2,5 г на 10 л); бордоская жидкость 1%. Повторить через 10–14 дней."),
        T("Нормировка завязей на персиках и абрикосах",
          "Удалять завязи вручную, оставляя 10–15 см между плодами. Проводить в фазе завязей размером с грецкий орех (3–4 недели после цветения)."),
        T("Высадка томатов, перца, баклажанов в открытый грунт (с 10–15 мая)",
          "Схема: томаты 60×50 см, перец 50×40 см, баклажан 60×40 см. После высадки притенить на 3–5 дней. Первый полив — через 3 дня. Замульчировать приствольный круг."),
        T("Пасынкование томатов",
          "Удалять пасынки при длине 3–5 см. В теплице — формировать в 1 стебель. В открытом грунте — в 2–3 стебля. Делать утром, чтобы срезы подсыхали за день."),
        T("Посев огурцов, кабачков, тыквы в открытый грунт",
          "Огурцы: глубина 2–3 см, схема 50×30 см. Кабачки: глубина 3–4 см, схема 70×70 см. Тыква: глубина 4–5 см, схема 100×100 см. Температура почвы — не ниже +15 °C."),
        T("Посадка однолетников в грунт"),
        T("Установка ловчих поясов на деревья",
          "Клеевые пояса (Во-Влаг, Argus, самодельные): ширина 20–25 см, крепить на высоте 40–60 см от земли. Обновлять клей каждые 4–6 недель."),
    ],
    "Июнь": [
        T("Сбор черешни и ранней клубники"),
        T("Обработка от плодожорки",
          "Препараты: Калипсо (3 мл на 10 л), Инсегар (5 г на 10 л), Герольд (6 мл на 10 л), Люфокс (10 мл на 10 л). Обрабатывать в период лёта бабочек, повторить через 12–14 дней."),
        T("Полив и подкормка деревьев в период жары",
          "Полив: 40–60 л на дерево, 20–30 л на куст раз в 7–10 дней. Подкормка: монофосфат калия (20 г на 10 л) или нитрофоска (30–40 г/м²)."),
        T("Прищипка побегов винограда, пасынкование",
          "Пасынки обламывать, оставляя 1–2 листа. Прищипку побегов проводить за 2–3 листа выше последней грозди."),
        T("Подкормка томатов, перца, огурцов",
          "В период цветения: монофосфат калия (15 г на 10 л) или Кемира Универсал (30 г на 10 л). Для томатов дополнительно кальциевая селитра (15–20 г на 10 л) — профилактика вершинной гнили. Огурцы: азотные удобрения (мочевина 10 г на 10 л)."),
        T("Прищипка и подкормка однолетних цветов",
          "Петуния, лобелия: прищипнуть отросшие побеги для ветвления. Подкормка раз в 10 дней жидким удобрением для цветущих (Агрикола, Fertika Люкс, монофосфат калия 10 г на 10 л)."),
        T("Сбор абрикосов в конце месяца"),
    ],
    "Июль": [
        T("Сбор персиков, ранних груш и яблок"),
        T("Летняя санитарная обрезка деревьев"),
        T("Подкормка плодовых фосфорно-калийными удобрениями",
          "Суперфосфат: 30–40 г/м². Сульфат калия: 20–30 г/м². Монофосфат калия: 20 г на 10 л (внекорневая). Калимагнезия: 20–25 г/м². Вносить с поливом."),
        T("Сбор малины, ежевики, голубики"),
        T("Борьба с паутинным клещом",
          "Препараты: Флумайт (2 мл на 10 л), Аполло (2 мл на 10 л), Санмайт (1 г на 10 л), Фитоверм (10 мл на 10 л — биопрепарат). Обрабатывать нижнюю сторону листьев, повторить через 7–10 дней."),
        T("Борьба с белокрылкой в теплице",
          "Препараты: Актара (1,4 г на 10 л), Конфидор Экстра (0,5 г на 10 л), Инсектор. Биопрепарат: Вертициллин. Развесить жёлтые клеевые ловушки для мониторинга. Повторить через 7 дней."),
        T("Пасынкование и подвязка томатов"),
        T("Сбор семян летников (ранние сорта)"),
    ],
    "Август": [
        T("Сбор поздних персиков, яблок, айвы в конце месяца"),
        T("Сбор инжира первого урожая"),
        T("Обрезка отплодоносивших побегов малины"),
        T("Посев сидератов на грядках",
          "Горчица белая: 3–5 г/м², заделать через 3–4 недели до цветения. Фацелия: 1,5–2 г/м². Редька масличная: 2–3 г/м². Рожь: 15–20 г/м² (под зиму)."),
        T("Посев двулетников на рассаду: виола, гвоздика турецкая, наперстянка",
          "Срок: август — начало сентября. Виола: температура прорастания 18–20 °C, всходы 7–14 дней. Рассаду высаживать в грунт в октябре для зимовки и цветения следующей весной."),
        T("Деление и пересадка многолетников",
          "Делить можно флоксы, хосты, астильбы, рудбекии, эхинацеи, лилейники. Оптимально — при пасмурной погоде, после спада жары. После деления полить и замульчировать."),
        T("Подготовка почвы под посадку многолетников"),
    ],
    "Сентябрь": [
        T("Сбор инжира второго урожая, айвы, поздних яблок"),
        T("Сбор актинидии и кизила"),
        T("Осенняя подкормка деревьев — фосфор и калий",
          "Суперфосфат двойной: 30–50 г/м² приствольного круга. Сульфат калия: 20–30 г/м². Древесная зола: 200–300 г/м². Без азотных удобрений!"),
        T("Посадка и деление многолетников",
          "Лучшее время для посадки флоксов, лилейников, хост, астильб, рудбекий. Делить кусты, поливать, мульчировать. До заморозков должно остаться не менее 4–6 недель."),
        T("Посадка луковичных цветов: тюльпаны, нарциссы, крокусы",
          "Тюльпаны: глубина 15–20 см, расстояние 10–15 см. Нарциссы: глубина 12–15 см. Крокусы: глубина 7–10 см. Почву заправить суперфосфатом (30 г/м²) и золой."),
        T("Посадка озимого чеснока",
          "Срок для Абинского района: конец сентября — начало октября. Схема: 15×8 см, глубина 6–8 см. Зубчики обработать Максимом (4 мл на 2 л воды) или замочить в розовом растворе марганцовки. Замульчировать соломой 5–7 см."),
        T("Уборка урожая: перец, баклажан, тыква, кабачок"),
    ],
    "Октябрь": [
        T("Влагозарядный полив деревьев",
          "Норма: 60–100 л на взрослое дерево, 30–50 л на молодое, 20–30 л на куст. Поливать медленно, в несколько приёмов. Цель — промочить почву на 60–80 см."),
        T("Осенняя обрезка кустарников"),
        T("Уборка однолетников, подготовка грядок",
          "Ботву больных растений — сжечь, здоровую — в компост. Грядки перекопать, внести перегной (5–8 кг/м²) или компост. Под томаты и перец — не сажать пасленовые культуры 3–4 года."),
        T("Укрытие голубики и актинидии на зиму",
          "Голубика: пригнуть ветви, укрыть агроволокном 60 г/м² в 2 слоя. Актинидия: снять с опор, уложить на лапник, укрыть агроволокном. Укрывать при устойчивых заморозках ниже −5 °C."),
        T("Укрытие теплолюбивых многолетников на зиму",
          "Канны, георгины, бегонии — выкопать, хранить в торфе при +5...+8 °C. Вербены, гелиотроп — укрыть агроволокном. Хризантемы — мульчировать слоем 10–15 см."),
        T("Санитарная обрезка многолетников",
          "Срезать засохшие стебли флоксов, рудбекий, эхинацей на высоту 10–15 см — для защиты корневища зимой. Хосты, астильбы, лилейники обрезать полностью."),
    ],
    "Ноябрь": [
        T("Побелка стволов деревьев",
          "Состав: 2–3 кг извести + 300 г медного купороса + 200 г казеинового клея на 10 л воды. Наносить кистью до высоты 1–1,5 м от земли."),
        T("Обвязка молодых деревьев от грызунов",
          "Материалы: металлическая сетка мелкоячеистая, рубероид, еловый лапник (иголками вниз), специальная лента от грызунов. Обвязывать от корневой шейки вверх на 50–80 см."),
        T("Последний влагозарядный полив",
          "Норма: 60–80 л на взрослое дерево. Проводить до промерзания почвы, при температуре +2...+5 °C."),
        T("Обработка теплицы на зиму",
          "Серная шашка (Климат, ФАС) — после уборки всех растений, форточки закрыть. Или промыть конструкции 1%-м медным купоросом (100 г на 10 л). Почву пролить горячей водой или фунгицидом."),
        T("Укрытие луковичных цветов при угрозе сильных морозов",
          "Тюльпаны и нарциссы в Абинском районе обычно зимуют без укрытия. При прогнозе ниже −15 °C — замульчировать слоем торфа или перегноя 8–10 см."),
        T("Уборка и хранение инструмента"),
    ],
    "Декабрь": [
        T("Санитарный осмотр деревьев, обрезка при необходимости"),
        T("Проверка укрытий"),
        T("Проверка хранения клубней и луковиц",
          "Георгины, канны, гладиолусы: температура +5...+8 °C, влажность 60–70%. Признаки проблем: мягкие пятна — гниль (удалить), сморщивание — пересохли (слегка опрыскать)."),
        T("Планирование следующего сезона и заказ семян",
          "Что заказывать заранее: редкие сорта томатов и перца, семена медленнорастущих цветов (виола, лобелия, петуния, сельдерей). Популярные культуры — доступны в феврале–марте."),
    ],
}

# ── HELPERS ───────────────────────────────────────────────────────────
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("API-ключ не найден. Проверь файл .env — должна быть строка ANTHROPIC_API_KEY=твой-ключ")
        st.stop()
    return anthropic.Anthropic(api_key=api_key, timeout=120.0)

def diagnose_photo(client, uploaded_file, extra_comment=""):
    image_bytes = uploaded_file.read()
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
    media_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    prompt = "Проанализируй это фото и определи что на нём: растение или сорт, болезнь, вредитель или что-то другое. Дай подробный ответ согласно структуре ответов из твоих правил."
    if extra_comment:
        prompt += f"\n\nКомментарий хозяйки: {extra_comment}"

    with st.spinner("Анализирую фото..."):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
        except anthropic.APITimeoutError:
            st.error("Превышено время ожидания. Попробуй ещё раз — иногда сервер отвечает медленнее обычного.")
            return None
        except anthropic.APIConnectionError:
            st.error("Нет соединения с сервером. Проверь интернет и попробуй снова.")
            return None
        except anthropic.APIStatusError as e:
            st.error(f"Ошибка API: {e.status_code}. Попробуй позже.")
            return None
    return response.content[0].text

def ask_agronomist(client, question, history=None):
    messages = []
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    with st.spinner("Думаю..."):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=messages,
            )
        except anthropic.APITimeoutError:
            st.error("Превышено время ожидания. Попробуй задать вопрос ещё раз.")
            return None
        except anthropic.APIConnectionError:
            st.error("Нет соединения с сервером. Проверь интернет и попробуй снова.")
            return None
        except anthropic.APIStatusError as e:
            st.error(f"Ошибка API: {e.status_code}. Попробуй позже.")
            return None
    return response.content[0].text

def render_tasks(tasks):
    parts = []
    for t in tasks:
        name = t["task"]
        details = t.get("details")
        if details:
            parts.append(
                f'<div class="task-item has-details">'
                f'<details><summary>'
                f'<span class="task-dot-arrow">▸</span>{name}'
                f'</summary>'
                f'<div class="task-details">{details}</div>'
                f'</details></div>'
            )
        else:
            parts.append(
                f'<div class="task-item"><span class="task-dot">◦</span>{name}</div>'
            )
    st.markdown("".join(parts), unsafe_allow_html=True)

# ── UI ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Садовый помощник</div>
    <div class="hero-sub">Краснодарский край · Абинский район · Предгорная&nbsp;зона</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Фото", "Календарь", "Агроном"])

st.components.v1.html("""<script>
(function() {
    const tips = [
        'Сделай фото и напиши свой вопрос по растению',
        'Календарь работ в саду',
        'Спроси у агронома'
    ];
    function apply() {
        const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        tabs.forEach((t, i) => { if (tips[i]) t.title = tips[i]; });
    }
    apply();
    const mo = new MutationObserver(apply);
    mo.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>""", height=0)

# ── Вкладка 1: Фото-диагностика ──────────────────────────────────────
with tab1:
    st.markdown('<div class="tab-hint">Загрузи фото или сними прямо сейчас — получишь диагноз и рекомендации.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Загрузи фото",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="camera-divider">— или сними сейчас —</div>', unsafe_allow_html=True)

    camera_photo = st.camera_input("Камера", label_visibility="collapsed")

    image_source = camera_photo or uploaded_file

    if image_source:
        if uploaded_file and not camera_photo:
            st.image(uploaded_file, caption="Фото для анализа", use_container_width=True)
        st.markdown('<div class="action-panel"><div class="action-panel-label">Дополнительное описание (необязательно)</div>', unsafe_allow_html=True)
        extra_comment = st.text_input(
            "Дополнительное описание",
            placeholder="Например: желтеют листья у персика, появились три недели назад",
            label_visibility="collapsed"
        )
        if st.button("Определить", type="primary", use_container_width=True):
            client = get_client()
            image_source.seek(0)
            result = diagnose_photo(client, image_source, extra_comment)
            if result:
                st.markdown('<div class="result-label">Результат диагностики</div>', unsafe_allow_html=True)
                st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)
        st.components.v1.html("""<script>
(function(){
    var doc = window.parent.document;
    if(window.parent.innerWidth > 768) return;
    function findMain(){
        return Array.from(doc.querySelectorAll('button')).find(function(b){
            return b.textContent.trim()==='Определить' && b.id!=='garden-fab';
        });
    }
    function addFab(){
        if(doc.getElementById('garden-fab')) return;
        if(!findMain()) return;
        var fab = doc.createElement('button');
        fab.id = 'garden-fab';
        fab.textContent = 'Определить';
        fab.style.cssText = [
            'position:fixed','bottom:1.2rem','left:1rem','right:1rem',
            'width:calc(100% - 2rem)',
            'background:linear-gradient(135deg,#0d9488,#0f766e)',
            'color:#fff','border:none','border-radius:12px',
            'padding:.9rem','font-size:1rem','font-weight:600',
            'font-family:Inter,sans-serif',
            'box-shadow:0 -2px 28px rgba(13,148,136,.38)',
            'z-index:9999','cursor:pointer'
        ].join(';');
        fab.onclick = function(){
            var m = findMain();
            if(m) m.click();
        };
        doc.body.appendChild(fab);
    }
    setTimeout(addFab, 350);
    var mo = new MutationObserver(function(){
        var hasMain = !!findMain();
        var fab = doc.getElementById('garden-fab');
        if(hasMain && !fab) addFab();
        if(!hasMain && fab) fab.remove();
    });
    mo.observe(doc.body, {childList:true, subtree:true});
})();
</script>""", height=0)
    else:
        st.components.v1.html("""<script>
(function(){
    var fab = window.parent.document.getElementById('garden-fab');
    if(fab) fab.remove();
})();
</script>""", height=0)

# ── Вкладка 2: Сезонный календарь ────────────────────────────────────
with tab2:
    st.markdown('<div class="tab-hint">Мероприятия по месяцам для твоего участка в Абинском районе.</div>', unsafe_allow_html=True)

    month_names_ru = list(CALENDAR.keys())
    month_map = {
        "January": "Январь", "February": "Февраль", "March": "Март",
        "April": "Апрель", "May": "Май", "June": "Июнь",
        "July": "Июль", "August": "Август", "September": "Сентябрь",
        "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь"
    }
    current_month_ru = month_map.get(datetime.now().strftime("%B"), "Июнь")
    default_index = month_names_ru.index(current_month_ru)

    selected_month = st.selectbox("Выбери месяц", month_names_ru, index=default_index)

    st.markdown(f'<div class="month-title">{selected_month}</div>', unsafe_allow_html=True)
    render_tasks(CALENDAR[selected_month])

    st.divider()

    if st.toggle("Показать весь год"):
        for month, tasks in CALENDAR.items():
            with st.expander(month):
                render_tasks(tasks)

# ── Вкладка 3: Спросить агронома ─────────────────────────────────────
with tab3:
    st.markdown('<div class="tab-hint">Задай любой вопрос про свой участок — по уходу, подкормкам, посадкам, болезням.</div>', unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    avatars = {"user": "🧑", "assistant": "🌿"}
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar=avatars[msg["role"]]):
            st.write(msg["content"])

    with st.form("chat_form", clear_on_submit=True):
        question = st.text_area(
            "Вопрос",
            placeholder="Спроси что-нибудь...",
            height=80,
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Спросить агронома", use_container_width=True, type="primary")

    if submitted and question.strip():
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="🧑"):
            st.write(question)

        client = get_client()
        answer = ask_agronomist(client, question, st.session_state.chat_history[:-1])

        if answer:
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant", avatar="🌿"):
                st.write(answer)
            st.rerun()

