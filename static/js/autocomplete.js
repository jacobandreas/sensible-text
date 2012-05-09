/* globals */
var selected_sources = []
var currentReq;
var currentTimeout;
var completions;
var completionIndex;

/* source management */
function toggleSource(name) {
  if (selected_sources.indexOf(name) === -1) {
    selectSource(name);
  } else {
    unselectSource(name);
  }
}
function selectSource(name) {
  selected_sources.push(name);
  $('#' + name).addClass('selected');
}
function unselectSource(name) {
  selected_sources = $.grep(selected_sources, function(val) {
    return val != name;
  });
  $('#' + name).removeClass('selected');
}
function getSourcesList() {
  return selected_sources.join(',');
}

/* autocomplete */
function getCurrentTrigram() {
  var rangeEnd = rangy.getSelection().getRangeAt(0).startOffset;
  var searchString = $('#text').text().substring(0, rangeEnd);
  var re = /(\w+\s){1,3}$/;
  var match = re.exec(searchString); 
  if (!match) {
    return '';
  }
  var str = match[0];
  return str.substring(0, str.length - 1);
}
function insertAtCursor(data) {
  var rangeEnd = rangy.getSelection().getRangeAt(0).startOffset;
  var before = $('#text').text().substring(0, rangeEnd);
  var after = $('#text').text().substring(rangeEnd);
  $('#text').text(before + data + after);
  var node = $('#text').contents()[0];
  var newrange = rangy.createRange();
  newrange.setStart(node, before.length);
  newrange.setEnd(node, before.length + data.length);
  rangy.getSelection().setSingleRange(newrange);
}
function showNextCompletion() {
  rangy.getSelection().getRangeAt(0).deleteContents();
  insertAtCursor(completions[completionIndex++]);
  completionIndex %= completions.length;
}

/* setup */
function setupEvents() {
  $('#text').keydown(function(evt) {
    if (!(evt.which === 8 || evt.which == 17 || evt.ctrlKey)) {
      var newrange = rangy.getSelection().collapseToEnd();
    }
  });
  $('#text').keyup(function(evt) {
    if (currentReq) {
      currentReq.abort();
      currentReq = null;
      completions = null;
      $('#spinner').hide();
    }
    if (currentTimeout) {
      clearTimeout(currentTimeout);
      currentTimeout = null;
    }
    if (evt.which === 32) {
      if (evt.ctrlKey && completions) {
        showNextCompletion();
        return;
      }
      setTimeout(function() {
        var ct = getCurrentTrigram();
        if (ct === '') {
          return;
        }
        $('#spinner').show()
        currentReq = $.get('/complete',
              {'sources': getSourcesList(), 'context': ct},
              function(data) {
          currentReq = null;
          $('#spinner').hide()
          if (data.length === 0) {
            return;
          }
          completions = data;
          completionIndex = 0;
          //showNextCompletion();
        });
      }, 500);
    }
  });
  $('#sources li').each(function() {
    $(this).click(function() {
      toggleSource(this.id);
    });
  });
}
function setupSpinner() {
  var spinner_opts = {
    lines: 7,
    length: 0,
    width: 4,
    radius: 8,
    rotate: 9,
    color: '#fff',
    speed: 1.4,
    trail: 60,
    shadow: false,
    hwaccel: false,
    className: 'spinner',
    zIndex: 2e9,
    top: 'auto',
    left: 'auto'
  }
  var spinner_target = document.getElementById('spinner');
  var spinner = new Spinner(spinner_opts).spin(spinner_target);
  $('#spinner').hide();
}

/* init */
$(document).ready(function() {
  selectSource('google');
  setupEvents();
  setupSpinner();
  $('#text').focus();
});
