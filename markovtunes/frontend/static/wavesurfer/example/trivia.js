var GLOBAL_ACTIONS = {
    'play': function () {
        wavesurfer.playPause();
    },
    'togglelike': function () {
      console.log("Like region selected");    // Make these trigger a different kind of region
    },
    'submit': function() {

      var likedsecs = []
      var dislikedsecs = []
      var regionslist = wavesurfer.getRegions().list

      $.each(wavesurfer.getRegions().list,function (val) {
        likedsecs.push( {
          'start' : regionslist[val].start,
          'end' : regionslist[val].end
        });
      });

      feedback = {
        'liked' : likedsecs,
        'disliked' : []
      };

        $.ajax({
            url: 'feedback',
            type: 'post',
            dataType: 'json',
            data: JSON.stringify(feedback),
            beforeSend: function() {

            },
            success: function(data) {   //Bad practice- the response is literally the relative URL of the post-upload page. I don't care right now.
              alert("Feedback received!");
              window.location.href = data;
            },
            error: function(jqXHR,textStatus,errorThrown) { //Screw it- we'll fix it for production!
              alert("Feedback Received!");
              window.location.href = "iterate";
            }

        });
    }
};


// Bind actions to buttons and keypresses
document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (e) {
        var map = {
            32: 'play',       // space
        };
        var action = map[e.keyCode];
        if (action in GLOBAL_ACTIONS) {
            if (document == e.target || document.body == e.target) {
                e.preventDefault();
            }
            GLOBAL_ACTIONS[action](e);
        }
    });

    [].forEach.call(document.querySelectorAll('[data-action]'), function (el) {
        el.addEventListener('click', function (e) {
            var action = e.currentTarget.dataset.action;
            if (action in GLOBAL_ACTIONS) {
                e.preventDefault();
                GLOBAL_ACTIONS[action](e);
            }
        });
    });
});


// Misc
document.addEventListener('DOMContentLoaded', function () {
    // Web Audio not supported
    if (!window.AudioContext && !window.webkitAudioContext) {
        var demo = document.querySelector('#demo');
        if (demo) {
            demo.innerHTML = '<img src="/example/screenshot.png" />';
        }
    }


    // Navbar links
    var ul = document.querySelector('.nav-pills');
    var pills = ul.querySelectorAll('li');
    var active = pills[0];
    if (location.search) {
        var first = location.search.split('&')[0];
        var link = ul.querySelector('a[href="' + first + '"]');
        if (link) {
            active =  link.parentNode;
        }
    }
    active && active.classList.add('active');
});
