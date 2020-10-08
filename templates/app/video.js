const NETWORK_STATE = {
    OK: 1,
    LOADING: 2,
    NOT_FOUND: 3
};

function VideoProcessing() {
    let player = $("#videoPlayer");
    let vidSrc = $("#vidSrc");
    const urlPrefix = "http://localhost:8000/static/videos";
    const urlSuffix = ".mp4";
    const urlLetterSuffix = "-abc.mp4";
    let sources = [];
    let currentVideoTrack = 0;
    let arrWords = [];
    let retryCounter = 0;

    this.processVideo = function(words) {
        arrWords = words;
        prepareUrls();
        vidSrc.attr('src', sources[currentVideoTrack]);
        player.on('ended', videoHandler);
        playVideo();
    }


    var prepareUrls = function() {
        sources = [];
        arrWords.forEach(strWord => {
            strWord = strWord.toLowerCase();
            let videoURl = "";
            if(strWord.length === 1) {
                videoURl = `${urlPrefix}/${strWord}${urlLetterSuffix}`;
            } else {
                videoURl = `${urlPrefix}/${strWord}${urlSuffix}`;
            }
            sources.push(videoURl);
        });
    }
    
    var videoHandler = function (e) {
        if(!e) {
           e = window.event; 
        }

        currentVideoTrack += 1;

        if(currentVideoTrack > sources.length - 1) return;
        
        $(vidSrc).attr('src', sources[currentVideoTrack]);
        playVideo();
     }

     var makeLetters = function () {
        const word = arrWords[currentVideoTrack];
    
        let remainingarr = arrWords.splice(currentVideoTrack + 1, arrWords.length);
        arrWords = [...arrWords, ...word.split(""), ...remainingarr];
        prepareUrls();
     }
 

    var playVideo = function() {
        player[0].load();
        // console.log(player[0].readyState)

        setTimeout(() => {
            
            let networkState = player[0].networkState;
            if(networkState === NETWORK_STATE.OK) {
                player[0].play();
                retryCounter = 0;
            } 
            else if(networkState === NETWORK_STATE.NOT_FOUND){
                if(arrWords[currentVideoTrack].length !== 1) {
                    makeLetters();
                }

                player.trigger("ended");
                retryCounter = 0;
            } else if(networkState === NETWORK_STATE.LOADING) {
                if(retryCounter === 3) {
                    player.trigger("ended");
                    retryCounter = 0;
                    return;
                }

                retry();
            }
        }, 500);
    }

    var retry = function() {
        setTimeout(()=>{
            retryCounter +=1;
            playVideo();
        }, 1500); 
    } 

}

function VoiceProcessing() {
   let control = $("#inputVoice");
   let inputText = null;

   this.getText = function() {
       inputText = control.val();
       return inputText;
   }

   this.getWords = function () {
       return inputText.split(" ");
   }
}


$("#showSigns").click(function(){    
    const objVoice = new VoiceProcessing();
    const objVideo = new VideoProcessing();
    objVoice.getText();
    const arrWords = objVoice.getWords();
    objVideo.processVideo(arrWords);
});

// var vid = document.getElementById("webCam");
// var mp4Vid = document.getElementById('mp4Source');
//     $(mp4Vid).attr('src', "https://www.handspeak.com/word/c/are-abc.mp4");
// vid.load();
// setTimeout(function() {
//     alert(vid.networkState);
// }, 3000);


// $("#showSigns").click(function(){

//     let inputVoice = $("#inputVoice").val();

//     let words = inputVoice.split(" ");

//     let sources = [];

//     words.forEach(word => {
//         let tempSrc = startUrl + "/" + word.charAt(0) + "/" + word + ".mp4";
//         sources.push(tempSrc)
//     });

//     console.log(sources);


//     // sources = [
//     //     "https://www.handspeak.com/word/b/b-abc.mp4",
//     //     "https://www.handspeak.com/word/c/c-abc.mp4",
//     //     "https://www.handspeak.com/word/a/a-abc.mp4",
//     //     "https://www.handspeak.com/word/d/d-abc.mp4"
//     // ];
    
    
//     var player = document.getElementById('webCam');
//     player.play();
    
//     var mp4Vid = document.getElementById('mp4Source');
    
//     $(mp4Vid).attr('src', sources[0]);
    
//     player.addEventListener('ended', myHandler, false);

//     var count = 0;
    
    
    // function myHandler(e) {

    //     if(sources.length < count) {
    //         return;
    //     } 
    
    //    if(!e) 
    //    {
    //       e = window.event; 
    //    }
    //    count++;
    //    $(mp4Vid).attr('src', sources[count]);
    //    player.load();
    //    player.play();
    // }
    
// });



