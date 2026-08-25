const QUESTIONS = [
  'Who would survive longest in prison?',
  'Who would be the best spy?',
  'Who would survive a zombie apocalypse?'
];

const rankList = document.getElementById('rankList');
const guessSelect = document.getElementById('guessSelect');
const submitRankingButton = document.getElementById('submitRanking');
const submitGuessButton = document.getElementById('submitGuess');

if (rankList) {
  new Sortable(rankList, { animation: 150 });
}

if (guessSelect) {
  QUESTIONS.forEach((question) => {
    const option = document.createElement('option');
    option.value = question;
    option.textContent = question;
    guessSelect.appendChild(option);
  });
}

let score = 0;
const correctQuestion = QUESTIONS[0];

submitRankingButton?.addEventListener('click', () => {
  const ranking = [...rankList.children].map((li) => li.textContent);
  const rankingSection = document.getElementById('ranking');
  const guessSection = document.getElementById('guess');
  const display = document.getElementById('rankingDisplay');

  rankingSection.classList.add('hidden');
  guessSection.classList.remove('hidden');
  display.innerHTML = '';

  ranking.forEach((name) => {
    const li = document.createElement('li');
    li.textContent = name;
    display.appendChild(li);
  });
});

submitGuessButton?.addEventListener('click', () => {
  const guess = document.getElementById('guessSelect').value;
  if (guess === correctQuestion) {
    score += 5;
  }

  document.getElementById('guess').classList.add('hidden');
  document.getElementById('results').classList.remove('hidden');
  document.getElementById('score').textContent = score;
});
