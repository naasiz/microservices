const analyzerStatsEl = document.getElementById('analyzerStats');
const processingStatsEl = document.getElementById('processingStats');
const quizEventEl = document.getElementById('quizEvent');
const questionEventEl = document.getElementById('questionEvent');

const analyzerUrl = 'http://20.163.57.7:8110/stats';
const processingUrl = 'http://20.163.57.7:8100/stats';
const quizEventUrl = 'http://20.163.57.7:8110/quiz-event?index=0';
const questionEventUrl = 'http://20.163.57.7:8110/question-event?index=0';

function fetchStats(url, element) {
  fetch(url)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      element.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
      element.textContent = `Error fetching data: ${error}`;
    });
}

// Fetch stats every 5 seconds
setInterval(() => {
  fetchStats(analyzerUrl, analyzerStatsEl);
  fetchStats(processingUrl, processingStatsEl);
  fetchStats(quizEventUrl, quizEventEl);
  fetchStats(questionEventUrl, questionEventEl);
}, 5000);

// Initial fetch
fetchStats(analyzerUrl, analyzerStatsEl);
fetchStats(processingUrl, processingStatsEl);
fetchStats(quizEventUrl, quizEventEl);
fetchStats(questionEventUrl, questionEventEl);
