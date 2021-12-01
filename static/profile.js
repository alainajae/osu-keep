window.addEventListener('load', function() {
    loadScores()
    loadComments()
});

// Loads scores
async function loadScores() {
    const scoreTable = document.getElementById('score-table-body');

    // Get scores from Flask
    const scores = await fetch('/get-scores')
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

    //Reset comments for rebuilding
    commentSection.innerHTML = ''

    for (let i = 0; i < Object.keys(comments).length; i++) {
        commentSection.innerHTML += 
        `
        <tr>
            <td class="comment"> 
                <span style="color: #585858;">
                    ${comments[i]['user']} @ ${comments[i]['time']}:
                </span>
                <br>
                >${comments[i]['text']}
            </td>
        </tr>
        `
    }
}

// POSTs a comment message to Flask and updates comment section
async function postComment() {
    commentText = document.getElementById('comment-text')
    posting = document.getElementById('posting') // Placeholder element that tells the user comment is posting
    console.log(posting.innerHTML)
    posting.innerText = 'Posting...'
    console.log(posting.innerHTML)

    const comments = await fetch("/create-comment", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
          message: commentText.value
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        return data;
    });
    
    loadComments(comments)
    posting.innerText = ''
    commentText.value = '';
}

//This isn't built into Javascript for whatever reason
function isEmpty(obj) {
    for (const i in obj) return false;
    return true;
}