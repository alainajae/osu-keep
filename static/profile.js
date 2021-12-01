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
async function loadComments() {
    const commentSection = document.getElementById('comments');

    const comments = await fetch('/get-comments')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            return data;
        });

    if (Object.keys(comments).length == 0) {
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
    console.log("finished")
}

// POSTs a comment message to Flask and updates comment section
async function postComment() {
    fetch("/create-comment", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
          message: document.getElementById('comment-text')['value']
        })
    })
    
    loadComments()
    document.getElementById("comment-text").value = '';
}