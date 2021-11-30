window.addEventListener('load', function() {
    load_scores()
    load_comments()
});

// Handles loading scores into DOM
async function load_scores() {
    const scores = await fetch('/get-scores')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            return data;
        });
    
    console.log(scores)

    const scoreTable = document.getElementById('score-table-body');

    for (let i = 0; i < Object.keys(scores).length; i++) {
        const beatmapSet = scores[i]['beatmapset']
        const diffName = scores[i]['beatmap']['version']
        const beatmapTitle = `${beatmapSet['artist']} - ${beatmapSet['title']} [${diffName}] // ${beatmapSet['creator']}` //Format: ARTIST - TITLE [DIFFNAME] // MAPPER
        const acc = Math.round(10000 * scores[i]['accuracy']) / 100; 

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

// Handles loading comments into DOM
async function load_comments() {
    const comments = await fetch('/get-comments')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            return data;
        });
    
    console.log(comments)

    const commentSection = document.getElementById('comments');

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