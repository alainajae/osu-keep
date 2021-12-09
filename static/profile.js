window.addEventListener('load', function() {
    loadScores()
    loadComments()
});

// Loads scores
async function loadScores() {
    const scoreTable = document.getElementById('score-table-body');
    const user_id = parseInt(document.getElementById('user-title').dataset.user)
    // Get scores from Flask
    const scores = await fetch('/get-scores', {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'user-id': user_id
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        return data;
    });
    
    scoreTable.innerHTML = ''

    for (let i = 0; i < Object.keys(scores).length; i++) {
        const beatmapSet = scores[i]['beatmapset']
        const diffName = scores[i]['beatmap']['version']
        const beatmapTitle = `${beatmapSet['artist']} - ${beatmapSet['title']} [${diffName}] // ${beatmapSet['creator']}` //Format: ARTIST - TITLE [DIFFNAME] // MAPPER
        const acc = (Math.round(10000 * scores[i]['accuracy']) / 100).toFixed(2); 

        scoreTable.innerHTML += 
        `
        <tr>
            <td>${i + 1}</td>
            <td>${scores[i]['rank']}</td>
            <td>${beatmapTitle}</td>
            <td>${acc}%</td>
            <td>${scores[i]['max_combo']}x</td>
            <td>${scores[i]['pp']}</td>
        </tr>
        `
    }
}


// Loads comment section
async function loadComments(comments={}) {
    const commentSection = document.getElementById('comments');
    //First see if comments are passed in
    if (isEmpty(comments)) {
        //If not then fetch them from Flask
        comments = await fetch('/get-comments')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            return data;
        });

        //If its still empty, then no comments have been made
        if (isEmpty(comments)) {
            commentSection.innerHTML = 
            `
            <tbody>
                <tr>
                    <td class="placeholder"> 
                        No comments yet
                    </td>
                </tr>
            <tbody>
            `

            return
        }
    }

    commentSection.innerHTML = '' //Reset comments for rebuilding

    for (let i = 0; i < Object.keys(comments).length; i++) {
        commentSection.innerHTML += 
        `
        <tr>
            <td class="comment">
                    ${comments[i]['user']} @ ${comments[i]['time']}:
                <br>
                >${comments[i]['text']}
            </td>
        </tr>
        `
    }
}

//POSTs a comment message to Flask and updates comment section
async function postComment() {
    commentText = document.getElementById('comment-text')
    posting = document.getElementById('posting') //Placeholder element that tells the user comment is posting
    posting.innerText = 'Posting...' //Show user that comment is posting


    //POST Request to Flask to create comment and then returns a JSON of new comments
    const comments = await fetch("/create-comment", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: commentText.value})
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        return data;
    });
    
    //Load comments into DOM and reset submission form
    loadComments(comments)
    posting.innerText = ''
    commentText.value = '';
}

//This isn't built into Javascript for whatever reason
function isEmpty(obj) {
    for (const i in obj) return false;
    return true;
}


function sortTableByColumn(table, column, asc = true) {
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    // Sort each row
    const sortedRows = rows.sort((a, b) => {
        const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
        const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();       
        return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    });

    // Remove all existing TRs from the table
    while (tBody.firstChild) {
        tBody.removeChild(tBody.firstChild);
    }

    // Re-add the newly sorted rows
    tBody.append(...sortedRows);

    // Remember how the column is currently sorted
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc)
}

Array.from(document.getElementsByClassName("header-sortable")).forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAscending = headerCell.classList.contains("th-sort-asc");

        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });
});
