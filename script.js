const canvas = document.querySelector("#game-canvas");
const ctx = canvas.getContext("2d");

const playerScoreEl = document.querySelector("#player-score");
const cpuScoreEl = document.querySelector("#cpu-score");

const state = {
  playerScore: 0,
  cpuScore: 0,
  isPaused: false,
  lastTime: 0,
};

const court = {
  width: canvas.width,
  height: canvas.height,
};

const paddle = {
  width: 16,
  height: 110,
  speed: 360,
};

const player = {
  x: 32,
  y: court.height / 2 - paddle.height / 2,
  velocity: 0,
};

const cpu = {
  x: court.width - 32 - paddle.width,
  y: court.height / 2 - paddle.height / 2,
  velocity: 0,
};

const ball = {
  radius: 10,
  x: court.width / 2,
  y: court.height / 2,
  speed: 300,
  vx: 1,
  vy: 0,
};

const keys = new Set();

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

const resetBall = (direction = 1) => {
  ball.x = court.width / 2;
  ball.y = court.height / 2;
  ball.speed = 300;
  ball.vx = direction;
  ball.vy = (Math.random() * 2 - 1) * 0.6;
};

const updateScores = () => {
  playerScoreEl.textContent = state.playerScore;
  cpuScoreEl.textContent = state.cpuScore;
};

const resetGame = () => {
  state.playerScore = 0;
  state.cpuScore = 0;
  updateScores();
  player.y = court.height / 2 - paddle.height / 2;
  cpu.y = court.height / 2 - paddle.height / 2;
  resetBall(Math.random() > 0.5 ? 1 : -1);
};

const handleInput = () => {
  player.velocity = 0;
  if (keys.has("ArrowUp") || keys.has("KeyW")) {
    player.velocity = -paddle.speed;
  }
  if (keys.has("ArrowDown") || keys.has("KeyS")) {
    player.velocity = paddle.speed;
  }
};

const updatePaddles = (delta) => {
  player.y += player.velocity * delta;
  player.y = clamp(player.y, 0, court.height - paddle.height);

  const target = ball.y - paddle.height / 2;
  const diff = target - cpu.y;
  cpu.velocity = clamp(diff * 2, -paddle.speed * 0.75, paddle.speed * 0.75);
  cpu.y += cpu.velocity * delta;
  cpu.y = clamp(cpu.y, 0, court.height - paddle.height);
};

const checkPaddleCollision = (paddleX, paddleY) => {
  return (
    ball.x - ball.radius < paddleX + paddle.width &&
    ball.x + ball.radius > paddleX &&
    ball.y + ball.radius > paddleY &&
    ball.y - ball.radius < paddleY + paddle.height
  );
};

const updateBall = (delta) => {
  ball.x += ball.vx * ball.speed * delta;
  ball.y += ball.vy * ball.speed * delta;

  if (ball.y - ball.radius <= 0 || ball.y + ball.radius >= court.height) {
    ball.vy *= -1;
    ball.y = clamp(ball.y, ball.radius, court.height - ball.radius);
  }

  if (checkPaddleCollision(player.x, player.y)) {
    ball.vx = Math.abs(ball.vx);
    const impact = (ball.y - (player.y + paddle.height / 2)) / (paddle.height / 2);
    ball.vy = clamp(impact, -1, 1);
    ball.speed = Math.min(ball.speed + 20, 520);
    ball.x = player.x + paddle.width + ball.radius;
  }

  if (checkPaddleCollision(cpu.x, cpu.y)) {
    ball.vx = -Math.abs(ball.vx);
    const impact = (ball.y - (cpu.y + paddle.height / 2)) / (paddle.height / 2);
    ball.vy = clamp(impact, -1, 1);
    ball.speed = Math.min(ball.speed + 20, 520);
    ball.x = cpu.x - ball.radius;
  }

  if (ball.x + ball.radius < 0) {
    state.cpuScore += 1;
    updateScores();
    resetBall(1);
  }

  if (ball.x - ball.radius > court.width) {
    state.playerScore += 1;
    updateScores();
    resetBall(-1);
  }
};

const drawCourt = () => {
  ctx.clearRect(0, 0, court.width, court.height);
  ctx.fillStyle = "rgba(255, 255, 255, 0.05)";
  ctx.fillRect(court.width / 2 - 2, 0, 4, court.height);

  ctx.setLineDash([12, 18]);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(court.width / 2, 0);
  ctx.lineTo(court.width / 2, court.height);
  ctx.stroke();
  ctx.setLineDash([]);
};

const drawPaddle = (x, y, color) => {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, paddle.width, paddle.height);
};

const drawBall = () => {
  ctx.fillStyle = "#66f2ff";
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  ctx.fill();
};

const drawPausedOverlay = () => {
  if (!state.isPaused) {
    return;
  }

  ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
  ctx.fillRect(0, 0, court.width, court.height);
  ctx.fillStyle = "#fff";
  ctx.font = "28px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("已暂停", court.width / 2, court.height / 2 - 10);
  ctx.font = "16px sans-serif";
  ctx.fillText("按空格继续", court.width / 2, court.height / 2 + 20);
};

const render = () => {
  drawCourt();
  drawPaddle(player.x, player.y, "#f8b500");
  drawPaddle(cpu.x, cpu.y, "#ff4d6d");
  drawBall();
  drawPausedOverlay();
};

const step = (timestamp) => {
  const delta = (timestamp - state.lastTime) / 1000;
  state.lastTime = timestamp;

  if (!state.isPaused) {
    handleInput();
    updatePaddles(delta);
    updateBall(delta);
  }

  render();
  window.requestAnimationFrame(step);
};

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    state.isPaused = !state.isPaused;
    return;
  }

  if (event.code === "KeyR") {
    resetGame();
    return;
  }

  keys.add(event.code);
});

window.addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

resetGame();
window.requestAnimationFrame(step);
