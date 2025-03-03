const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 10,
    dx: 2,
    dy: 2,
    speedMultiplier: 0.5
};

// Timer variables
let gameTime = 0;
let highScore = 0;
let timerInterval = setInterval(() => {
    gameTime++;
    document.getElementById("gameTime").innerText = `Game Time: ${gameTime}s`;
}, 1000);

// Generate obstacles
let obstacles = generateObstacles(3);

function generateObstacles(num) {
    let obs = [];
    for (let i = 0; i < num; i++) {
        obs.push({
            x: Math.random() * (canvas.width - 50),
            y: Math.random() * (canvas.height - 50),
            size: 40,
            speed: Math.random() * 2 + 1, // Random speed (1-3)
            direction: Math.random() < 0.5 ? 1 : -1
        });
    }
    return obs;
}

// Reset ball and obstacles on collision
function resetBallAndObstacle(obstacle) {
    // Update high score
    if (gameTime > highScore) {
        highScore = gameTime;
        document.getElementById("highScore").innerText = `Highest Record: ${highScore}s`;
    }

    // Reset game time
    gameTime = 0;

    // Reset ball
    ball.x = canvas.width / 2;
    ball.y = canvas.height / 2;
    ball.speedMultiplier = 0.5;

    // Reset obstacle
    obstacle.x = Math.random() * (canvas.width - 50);
    obstacle.y = Math.random() * (canvas.height - 50);
    obstacle.speed = Math.random() * 2 + 1;
    obstacle.direction = Math.random() < 0.5 ? 1 : -1;
}

// Update game frame
function updateGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Move ball
    ball.x += ball.dx * ball.speedMultiplier;
    ball.y += ball.dy * ball.speedMultiplier;

    // Bounce off walls
    if (ball.x - ball.radius < 0 || ball.x + ball.radius > canvas.width) ball.dx = -ball.dx;
    if (ball.y - ball.radius < 0 || ball.y + ball.radius > canvas.height) ball.dy = -ball.dy;

    // Draw ball
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = "blue";
    ctx.fill();
    ctx.closePath();

    // Move and draw obstacles
    ctx.fillStyle = "red";
    obstacles.forEach(obstacle => {
        obstacle.x += obstacle.speed * obstacle.direction;

        // Bounce obstacles off walls
        if (obstacle.x < 0 || obstacle.x + obstacle.size > canvas.width) {
            obstacle.direction *= -1;
        }

        ctx.fillRect(obstacle.x, obstacle.y, obstacle.size, obstacle.size);

        // Collision detection
        if (
            ball.x + ball.radius > obstacle.x &&
            ball.x - ball.radius < obstacle.x + obstacle.size &&
            ball.y + ball.radius > obstacle.y &&
            ball.y - ball.radius < obstacle.y + obstacle.size
        ) {
            resetBallAndObstacle(obstacle);
        }
    });

    requestAnimationFrame(updateGame);
}

// Function to update ball speed from EEG input
function setBallSpeed(multiplier) {
    ball.speedMultiplier = multiplier;
    document.getElementById("eegDisplay").innerText = `EEG Status: ${multiplier > 0.5 ? "BOOST MODE 🚀" : "Normal 🏁"}`;
}

// Start game loop
updateGame();
