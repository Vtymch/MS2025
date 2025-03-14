document.addEventListener("DOMContentLoaded", function () {
    const ashContainer = document.querySelector(".ash-container");
    const hamMenu = document.querySelector(".ham-menu");
    const offScreenMenu = document.querySelector(".off-screen-menu");

    if (!ashContainer) {
        console.error("Ошибка: контейнер .ash-container не найден!");
        return;
    }

    // Функция для создания пепла
    function createAsh(e) {
        if (!e || typeof e.pageX !== "number" || typeof e.pageY !== "number") {
            console.error("Ошибка: событие не содержит координат мыши", e);
            return;
        }

        const ash = document.createElement("div");
        ash.classList.add("ash");
        ash.style.left = `${e.pageX - 2}px`;
        ash.style.top = `${e.pageY - 2}px`;
        ash.style.setProperty('--i', Math.random() * 2 + 1);

        ashContainer.appendChild(ash);

        setTimeout(() => {
            ash.remove();
        }, 300);
    }

    // Убираем setInterval, потому что он вызывает createAsh без события e
    // setInterval(createAsh, 2000); ❌ 

    // Добавляем обработчик движения мыши
    document.addEventListener('mousemove', createAsh);

    // Обработчик гамбургер-меню
    hamMenu?.addEventListener("click", function () {
        hamMenu.classList.toggle("active");
        offScreenMenu?.classList.toggle("active");
    });

    // Проверяем протокол страницы
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://localhost:8000/ws`);

    // Когда WebSocket подключен
    ws.onopen = () => {
        console.log("Connected to WebSocket");
        ws.send("!The server is connected!");
    };

    // Когда сервер присылает сообщение
    ws.onmessage = (event) => {
        console.log("Server:", event.data);
    };

    // Обработка ошибок
    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    // Когда WebSocket закрывается
    ws.onclose = (event) => {
        console.log("WebSocket closed:", event);
    };
});
