const body = document.body;
const me = body.dataset.name;
const room = body.dataset.room;
const socket = io();

const lobbyScreen = document.getElementById('lobbyScreen');
const gameScreen = document.getElementById('gameScreen');
const readyButton = document.getElementById('ready');
const startButton = document.getElementById('start');
const roundEl = document.getElementById('round');
const hostView = document.getElementById('hostView');
const playerView = document.getElementById('playerView');
const resultView = document.getElementById('resultView');
const questionEl = document.getElementById('question');
const playersList = document.getElementById('players');
const rankPlayers = document.getElementById('rankPlayers');
const submitRankingBtn = document.getElementById('submitRankingBtn');
const playerRankingDisplay = document.getElementById('playerRankingDisplay');
const questionList = document.getElementById('questionList');
const submitGuessBtn = document.getElementById('submitGuessBtn');
const resultTitle = document.getElementById('resultTitle');
const resultMessage = document.getElementById('resultMessage');
const scoreboard = document.getElementById('scoreboard');
const nextRoundBtn = document.getElementById('nextRoundBtn');

let selectedGuess = null;
let currentHost = null;
let currentRanker = null;
let rankingLocked = false;
let guessLocked = false;
let sortableInstance = null;

socket.emit('join_room', { room, name: me });

readyButton.addEventListener('click', () => socket.emit('toggle_ready'));
startButton.addEventListener('click', () => socket.emit('start_game'));
submitRankingBtn.addEventListener('click', () => {
  if (rankingLocked) return;

  const ranking = [...rankPlayers.children].map((li) => li.dataset.name);
  if (!ranking.length) return;

  rankingLocked = true;
  submitRankingBtn.disabled = true;
  submitRankingBtn.textContent = 'Ranking submitted';
  rankPlayers.classList.add('hidden');

  const helper = hostView.querySelector('.helper-copy');
  if (helper) {
    helper.textContent = 'Waiting for players to pick their question...';
  }

  if (sortableInstance) {
    sortableInstance.option('disabled', true);
  }

  socket.emit('submit_ranking', { ranking });
});
submitGuessBtn.addEventListener('click', () => {
  if (!selectedGuess || guessLocked) return;

  guessLocked = true;
  questionList.classList.add('hidden');
  socket.emit('submit_guess', { guess: selectedGuess });
  submitGuessBtn.disabled = true;
  submitGuessBtn.textContent = 'Guess submitted';
});
nextRoundBtn.addEventListener('click', () => socket.emit('next_round'));

function renderQuestionChoices(questions) {
  questionList.innerHTML = '';
  questions.forEach((question) => {
    const option = document.createElement('button');
    option.type = 'button';
    option.className = 'question-option';
    option.textContent = question;
    option.addEventListener('click', () => {
      selectedGuess = question;
      document.querySelectorAll('.question-option').forEach((btn) => {
        btn.classList.toggle('selected', btn === option);
      });
    });
    questionList.appendChild(option);
  });
}

function renderScoreboard(entries) {
  scoreboard.innerHTML = '';
  entries.forEach((entry) => {
    const row = document.createElement('div');
    row.className = 'score-row';
    row.innerHTML = `<span>${entry.avatar || '🎮'} ${entry.name}</span><strong>${entry.score}</strong>`;
    scoreboard.appendChild(row);
  });
}

socket.on('lobby_update', (data) => {
  currentHost = data.host;
  currentRanker = data.ranker;
  playersList.innerHTML = '';
  let allReady = true;

  Object.entries(data.players).forEach(([name, info]) => {
    if (name !== data.host) {
      allReady = allReady && info.ready;
    }

    const item = document.createElement('li');
    const badge = document.createElement('span');
    badge.className = 'state';
    badge.textContent = info.ready ? 'Ready' : 'Waiting';

    const label = document.createElement('span');
    label.className = 'player-name';
    label.textContent = `${name === data.host ? '👑 ' : ''}${info.avatar || '🎮'} ${name}`;

    item.appendChild(label);
    item.appendChild(badge);
    playersList.appendChild(item);
  });

  if (me === data.host) {
    startButton.classList.remove('hidden');
    readyButton.classList.add('hidden');
    startButton.disabled = !allReady;
  } else {
    startButton.classList.add('hidden');
    readyButton.classList.remove('hidden');
  }

  if (data.scoreboard) {
    renderScoreboard(data.scoreboard);
  }
});

socket.on('game_started', (data) => {
  lobbyScreen.classList.remove('active-screen');
  lobbyScreen.classList.add('hidden');
  gameScreen.classList.add('active-screen');
  gameScreen.classList.remove('hidden');
  resultView.classList.add('hidden');
  roundEl.textContent = data.round;
  currentHost = data.host;
  currentRanker = data.ranker;

  if (me === data.ranker) {
    hostView.classList.remove('hidden');
    playerView.classList.add('hidden');
  } else {
    hostView.classList.add('hidden');
    playerView.classList.remove('hidden');
  }
});

socket.on('host_question', (data) => {
  rankingLocked = false;
  guessLocked = false;
  selectedGuess = null;
  questionList.classList.remove('hidden');
  questionList.innerHTML = '';
  submitRankingBtn.disabled = false;
  submitRankingBtn.textContent = 'Submit ranking';
  rankPlayers.classList.remove('hidden');

  const helper = hostView.querySelector('.helper-copy');
  if (helper) {
    helper.textContent = 'Drag and drop the players into your final ranking.';
  }

  questionEl.textContent = data.question;
  rankPlayers.innerHTML = '';

  data.players.forEach((player) => {
    const item = document.createElement('li');
    item.dataset.name = player;
    const name = document.createElement('span');
    name.className = 'ranking-player-name';
    name.textContent = player;
    item.appendChild(name);
    rankPlayers.appendChild(item);
  });

  if (window.Sortable && rankPlayers) {
    if (sortableInstance) {
      sortableInstance.destroy();
    }
    sortableInstance = new Sortable(rankPlayers, {
      animation: 150,
      ghostClass: 'sortable-ghost',
      dragClass: 'sortable-drag'
    });
  }
});

socket.on('ranking_submitted', (data) => {
  if (me === currentRanker) {
    const helper = hostView.querySelector('.helper-copy');
    if (helper) helper.textContent = 'Ranking sent. Waiting for every player to submit a guess.';
    return;
  }

  playerRankingDisplay.innerHTML = '';
  data.ranking.forEach((player) => {
    const item = document.createElement('li');
    item.textContent = player;
    playerRankingDisplay.appendChild(item);
  });

  selectedGuess = null;
  guessLocked = false;
  questionList.classList.remove('hidden');
  renderQuestionChoices(data.question_options || []);

  hostView.classList.add('hidden');
  playerView.classList.remove('hidden');
  resultView.classList.add('hidden');
  submitGuessBtn.disabled = false;
  submitGuessBtn.textContent = 'Submit guess';
});

socket.on('guess_received', (data) => {
  const helper = playerView.querySelector('.helper-copy');
  if (helper && me !== currentRanker) {
    helper.textContent = `Guess received. Waiting for all players: ${data.submitted}/${data.total}.`;
  }
});

socket.on('round_result', (data) => {
  const correctCount = Object.values(data.guesses).filter((guess) => guess.correct).length;
  resultTitle.textContent = 'Round complete';
  resultMessage.textContent = `${correctCount} of ${Object.keys(data.guesses).length} players guessed correctly. The question was: ${data.correct_question}`;
  renderScoreboard(data.scoreboard);

  hostView.classList.add('hidden');
  playerView.classList.add('hidden');
  resultView.classList.remove('hidden');
  nextRoundBtn.classList.toggle('hidden', me !== currentHost);
});

socket.on('next_round_started', (data) => {
  currentHost = data.host;
  currentRanker = data.ranker;
  rankingLocked = false;
  guessLocked = false;
  selectedGuess = null;
  roundEl.textContent = data.round;
  lobbyScreen.classList.remove('active-screen');
  lobbyScreen.classList.add('hidden');
  gameScreen.classList.remove('hidden');
  gameScreen.classList.add('active-screen');
  resultView.classList.add('hidden');
  questionList.classList.remove('hidden');

  if (me === data.ranker) {
    hostView.classList.remove('hidden');
    playerView.classList.add('hidden');
    submitRankingBtn.disabled = false;
    submitRankingBtn.textContent = 'Submit ranking';
  } else {
    hostView.classList.add('hidden');
    playerView.classList.remove('hidden');
    playerRankingDisplay.innerHTML = '';
    questionList.innerHTML = '';
    submitGuessBtn.disabled = false;
    submitGuessBtn.textContent = 'Submit guess';
  }
});
