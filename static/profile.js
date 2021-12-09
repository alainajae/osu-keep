window.addEventListener('load', function() {
    loadScores('score-table-body', '/get-scores')
    loadScores('recent-table-body', '/get-recent')
    loadCommentForm()
    loadComments()
});

// Loads scores
async function loadScores(element, endpoint) {
    const scoreTable = document.getElementById(element);
    const userID = parseInt(document.getElementById('user-title').dataset.user)
    // Get scores from Flask
    const scores = await fetch(endpoint, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'user-id': userID
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

function loadCommentForm() {
    const loggedIn = document.getElementById('login').innerText == "Logout"
    const commentForm = document.getElementById('comment-form')

    if (loggedIn) {
        commentForm.innerHTML = 
        `
        <h3 id="comment-header">Comments</h3>
        <form onsubmit="postComment();return false;">
            <input id="comment-text" type="text" name="text" placeholder="add a public comment...">
            <input id="submit" type="submit" value="Post">
        </form>
        <h4 id="posting"></h4>
        `
    }
    else {
        commentForm.innerHTML = 
        `
        <h3 id="comment-header">Log in to add comments</h3>
        `
    }
}


// Loads comment section
async function loadComments(comments={}) {
    const commentSection = document.getElementById('comments');
    const userID = parseInt(document.getElementById('user-title').dataset.user)
    //First see if comments are passed in
    if (isEmpty(comments)) {
        //If not then fetch them from Flask
        comments = await fetch('/get-comments', {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'user-id': userID
            }
        })
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
                    ${comments[i]['commenter']} @ ${comments[i]['time']}:
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
    const userID = parseInt(document.getElementById('user-title').dataset.user)

    //POST Request to Flask to create comment and then returns a JSON of new comments
    const comments = await fetch("/create-comment", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
          'message': commentText.value,
          'userID': userID
        })
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
