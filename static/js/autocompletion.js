// @ts-nocheck
const debounce = (callback, delay) => {
  let timerId;

  return (...args) => {
    clearTimeout(timerId);
    timerId = setTimeout(() => {
      callback.apply(this, args);
    }, delay);
  };
};

const inputField = document.querySelector('#query-field');
const resultsList = document.querySelector('#autocomplete-results');
let currentHighlight = -1;

const debounceAutocomplete = debounce((event) => {
  const query = event.target.value;
  if (query.length >= 3) {
    fetch(`/api/autocomplete?query=${query}`)
      .then(response => response.json())
      .then(data => {
        resultsList.innerHTML = '';
        currentHighlight = -1;

        console.log(data);
        // Check if data is an array
        if (Array.isArray(data.matches)) {

          // Populate the results in the dropdown
          data.matches.forEach((result, index) => {

            const li = document.createElement('li');
            const paperTitle = document.createElement('div');
            const authorsYear = document.createElement('div');
            paperTitle.classList.add('paperTitle');
            authorsYear.classList.add('authorsYear');
            paperTitle.innerText = result.title;
            authorsYear.innerText = result.authorsYear;
            li.addEventListener('click', () => {
              inputField.value = result.title;
              resultsList.innerHTML = '';
            });

            li.addEventListener('mouseover', () => {
              // Highlight item when mouseover
              highlightSuggestion(index);
            });

            li.appendChild(paperTitle);
            li.appendChild(authorsYear);
            resultsList.appendChild(li);
          });

          // Show the results dropdown if there are suggestions
          if (data.length > 0) {
            //resultsList.style.display = 'block';
          }
        } else {
          // Handle the case when data is not an array
          console.error('Invalid response format');
        }
      });
  } else {
    resultsList.innerHTML = '';
  }
  // Call your autocomplete API here with the query
  console.log(`Calling autocomplete API with query: ${query}`);
}, 300);

function highlightSuggestion(index) {
  const items = Array.from(resultsList.getElementsByTagName("li"));
  if (currentHighlight !== -1) {
    items[currentHighlight].classList.remove('highlighted');
  }
  if (index !== -1) {
    items[index].classList.add('highlighted');
    items[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  
  currentHighlight = index;
  console.log(index);
  console.log(items);
}

inputField.addEventListener('input', debounceAutocomplete);

inputField.addEventListener('keydown', function (event) {
  const items = Array.from(resultsList.getElementsByTagName("li"));
  switch (event.key) {
    case 'ArrowUp':
    console.log('ArrowUp is pressed');
      if (currentHighlight > 0) {
        highlightSuggestion(currentHighlight - 1);
      }else{
        highlightSuggestion(items.length- 1);
      }
      break;
    case 'ArrowDown':
      console.log('ArrowDown is pressed');
      if (currentHighlight < items.length - 1) {
        highlightSuggestion(currentHighlight + 1);
      }else{
        highlightSuggestion(0);
      }
      break;
    case 'Enter':
      if (currentHighlight !== -1) {
        items[currentHighlight].click();
      }
      break;
  }
});