const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const menuScreen = document.getElementById("menu-screen");
const playerNameInput = document.getElementById("playerName");
const startBtn = document.getElementById("startBtn");
const scoreList = document.getElementById("scoreList");

// --- НОВЫЕ РАЗМЕРЫ ПОД ХОЛСТ 600x600 ---
const box = 30; // Увеличили размер клетки (было 20)
const canvasSize = 600; // Размер холста
const gridSize = 20; // Количество клеток по сетке (осталось 20)

const FOOD_TYPES = [
    { shape: "square", color: "#ff3366" },   
    { shape: "circle", color: "#ffcc00" },   
    { shape: "triangle", color: "#00ccff" }, 
    { shape: "diamond", color: "#cc33ff" }   
];

let snake = [];
let eaten = [];
let d = "RIGHT"; 
let food;
let score = 0;
let gameOver = false;
let gameInterval;
let playerName = "Игрок";
let gameState = "menu"; 

function loadLeaderboard() {
    scoreList.innerHTML = ""; 
    let records = JSON.parse(localStorage.getItem("snakeHighScores")) || [];
    
    if (records.length === 0) {
        scoreList.innerHTML = "<li>Пока нет рекордов</li>";
        return;
    }

    records.forEach((rec, index) => {
        let li = document.createElement("li");
        if (index === 0) li.style.color = "#ffd700"; 
        li.innerText = `${rec.name} — ${rec.score} очков`;
        scoreList.appendChild(li);
    });
}

function saveScore() {
    let records = JSON.parse(localStorage.getItem("snakeHighScores")) || [];
    records.push({ name: playerName, score: score });
    records.sort((a, b) => b.score - a.score);
    records = records.slice(0, 5); 
    localStorage.setItem("snakeHighScores", JSON.stringify(records));
    loadLeaderboard();
}

function initGame() {
    snake = [{ x: 10 * box, y: 10 * box }];
    eaten = [{ shape: "square", color: "#00ff00" }];
    d = "RIGHT";
    score = 0;
    gameOver = false;
    food = generateFood();
}

function generateFood() {
    let randomType = FOOD_TYPES[Math.floor(Math.random() * FOOD_TYPES.length)];
    return {
        // Используем gridSize (20), чтобы еда появлялась ровно в клетках
        x: Math.floor(Math.random() * gridSize) * box,
        y: Math.floor(Math.random() * gridSize) * box,
        shape: randomType.shape,
        color: randomType.color
    };
}

startBtn.addEventListener("click", () => {
    let name = playerNameInput.value.trim();
    if (name === "") {
        alert("Пожалуйста, введи своё имя!");
        return;
    }
    playerName = name;
    menuScreen.style.display = "none"; 
    gameState = "playing";
    initGame();
    clearInterval(gameInterval); 
    gameInterval = setInterval(draw, 140); 
});

document.addEventListener("keydown", function(event) {
    let key = event.key;
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(key)) {
        event.preventDefault();
    }
    if (gameState !== "playing") return; 

    if (key === "ArrowLeft" && d !== "RIGHT") d = "LEFT";
    if (key === "ArrowUp" && d !== "DOWN") d = "UP";
    if (key === "ArrowRight" && d !== "LEFT") d = "RIGHT";
    if (key === "ArrowDown" && d !== "UP") d = "DOWN";
});

function collision(head, array) {
    for (let i = 0; i < array.length; i++) {
        if (head.x === array[i].x && head.y === array[i].y) return true;
    }
    return false;
}

function drawShape(x, y, shape, color, isHead, isFood) {
    ctx.save(); 
    
    ctx.shadowColor = color;
    ctx.shadowBlur = isFood ? 20 : 12; // Увеличили свечение
    
    let pulse = isFood ? Math.sin(Date.now() / 150) * 3 : 0; 
    let size = box + pulse;
    let offset = (box - size) / 2;

    let gradient = ctx.createLinearGradient(x, y, x + size, y + size);
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, "#ffffff"); 

    ctx.fillStyle = gradient;
    ctx.strokeStyle = isHead ? "#ffffff" : color; 
    ctx.lineWidth = isHead ? 3 : 2; // Сделали обводку толще

    ctx.beginPath(); 
    
    if (shape === "square") {
        let r = 8; // Скругление углов побольше
        ctx.moveTo(x + offset + r, y + offset);
        ctx.lineTo(x + offset + size - r, y + offset);
        ctx.quadraticCurveTo(x + offset + size, y + offset, x + offset + size, y + offset + r);
        ctx.lineTo(x + offset + size, y + offset + size - r);
        ctx.quadraticCurveTo(x + offset + size, y + offset + size, x + offset + size - r, y + offset + size);
        ctx.lineTo(x + offset + r, y + offset + size);
        ctx.quadraticCurveTo(x + offset, y + offset + size, x + offset, y + offset + size - r);
        ctx.lineTo(x + offset, y + offset + r);
        ctx.quadraticCurveTo(x + offset, y + offset, x + offset + r, y + offset);
        ctx.closePath();
        ctx.fill();
        if (isHead) ctx.stroke();
    } 
    else if (shape === "circle") {
        ctx.arc(x + box/2, y + box/2, size/2, 0, Math.PI * 2);
        ctx.fill();
        if (isHead) ctx.stroke();
    } 
    else if (shape === "triangle") {
        ctx.moveTo(x + box/2, y + offset); 
        ctx.lineTo(x + offset + size, y + offset + size); 
        ctx.lineTo(x + offset, y + offset + size); 
        ctx.closePath();
        ctx.fill();
        if (isHead) ctx.stroke();
    } 
    else if (shape === "diamond") {
        ctx.moveTo(x + box/2, y + offset); 
        ctx.lineTo(x + offset + size, y + box/2); 
        ctx.lineTo(x + box/2, y + offset + size); 
        ctx.lineTo(x + offset, y + box/2); 
        ctx.closePath();
        ctx.fill();
        if (isHead) ctx.stroke();
    }
    
    ctx.restore(); 
}

function drawBackground() {
    let bgGradient = ctx.createLinearGradient(0, 0, canvasSize, canvasSize);
    bgGradient.addColorStop(0, "#1e1e2f");
    bgGradient.addColorStop(1, "#0f0c1b");
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, canvasSize, canvasSize);

    ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
    ctx.lineWidth = 1;
    for (let i = 0; i < canvasSize; i += box) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvasSize); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvasSize, i); ctx.stroke();
    }
}

function draw() {
    if (gameOver) return;

    drawBackground(); 

    for (let i = 0; i < snake.length; i++) {
        let isHead = (i === 0); 
        let info = eaten[i];
        drawShape(snake[i].x, snake[i].y, info.shape, info.color, isHead, false);
    }

    drawShape(food.x, food.y, food.shape, food.color, false, true);

    let snakeX = snake[0].x;
    let snakeY = snake[0].y;

    if (d === "LEFT") snakeX -= box;
    if (d === "UP") snakeY -= box;
    if (d === "RIGHT") snakeX += box;
    if (d === "DOWN") snakeY += box;

    if (snakeX < 0) snakeX = canvasSize - box;
    else if (snakeX >= canvasSize) snakeX = 0;
    if (snakeY < 0) snakeY = canvasSize - box;
    else if (snakeY >= canvasSize) snakeY = 0;

    let newHead = { x: snakeX, y: snakeY };

    if (snakeX === food.x && snakeY === food.y) {
        let currentMultiplier = Math.floor((eaten.length - 1) / 10) + 1;
        score += 10 * currentMultiplier;
        eaten.unshift({ shape: food.shape, color: food.color });
        food = generateFood(); 
    } else {
        snake.pop(); 
    }

    if (collision(newHead, snake)) {
        gameOver = true;
        clearInterval(gameInterval); 
        saveScore(); 
        
        ctx.fillStyle = "rgba(15, 12, 27, 0.9)";
        ctx.fillRect(0, 0, canvasSize, canvasSize);
        
        ctx.font = "bold 50px Montserrat"; // Увеличили шрифт
        ctx.fillStyle = "#ff3366";
        ctx.shadowColor = "#ff3366";
        ctx.shadowBlur = 25;
        ctx.textAlign = "center";
        ctx.fillText("ИГРА ОКОНЧЕНА", canvasSize / 2, canvasSize / 2 - 30);
        
        ctx.shadowBlur = 0; 
        ctx.font = "24px Montserrat";
        ctx.fillStyle = "white";
        ctx.fillText("Очки: " + score, canvasSize / 2, canvasSize / 2 + 30);
        ctx.fillStyle = "#00ffcc";
        ctx.fillText("Кликни, чтобы выйти в меню", canvasSize / 2, canvasSize / 2 + 80);
        return;
    }

    snake.unshift(newHead);

    let displayMultiplier = Math.floor((eaten.length - 1) / 10) + 1;
    ctx.fillStyle = "white";
    ctx.font = "bold 24px Montserrat"; // Увеличили шрифт
    ctx.textAlign = "left";
    ctx.fillText("Очки: " + score, 20, 40);
    
    ctx.fillStyle = "#ffcc00";
    ctx.textAlign = "right";
    ctx.fillText("Бонус: x" + displayMultiplier, canvasSize - 20, 40);
}

canvas.addEventListener("click", () => {
    if (gameState === "playing" && gameOver) {
        gameState = "menu";
        gameOver = false;
        menuScreen.style.display = "flex"; 
        playerNameInput.value = ""; 
    }
});

loadLeaderboard();