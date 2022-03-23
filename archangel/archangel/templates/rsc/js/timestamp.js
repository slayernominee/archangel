function convertTimestampToLocalDate(timestamp) {
    timestamp = parseInt(timestamp);
    var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
    yyyy = d.getFullYear(),
    mm = ('0' + (d.getMonth() + 1)).slice(-2),	// Months are zero based. Add leading 0.
    dd = ('0' + d.getDate()).slice(-2),			// Add leading 0.
    hh = d.getHours(),
    h = hh,
    min = ('0' + d.getMinutes()).slice(-2),		// Add leading 0.
    ampm = '',
    time;
    
    if (['en', 'en-US'].indexOf(navigator.language) >= 0) {
        // ie: 02/18/2013
        time = mm + '/' + dd + '/' + yyyy;
    } else if(['de', 'de-DE'].indexOf(navigator.language) >= 0) {
        // ie: 18.02.2013
        time = dd + '.' + mm + '.' + yyyy;
    } else if(['fr', 'fr-FR'].indexOf(navigator.language) >= 0) {
        // ie: 18/02/2013
        time = dd + '/' + mm + '/' + yyyy;
    } else if(['jp', 'jp-JP'].indexOf(navigator.language) >= 0) {
        // ie: 2013年02月18日
        time = yyyy + '年' + mm + '月' + dd +'日';
    } else {
        // ie: 2013-02-18
        time = yyyy + '-' + mm + '-' + dd;
    }
    
    return time;
}
function convertTimeStampToLocalDD_MM(timestamp) {
    timestamp = parseInt(timestamp);
    var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
    yyyy = d.getFullYear(),
    mm = ('0' + (d.getMonth() + 1)).slice(-2),	// Months are zero based. Add leading 0.
    dd = ('0' + d.getDate()).slice(-2),			// Add leading 0.
    hh = d.getHours(),
    h = hh,
    min = ('0' + d.getMinutes()).slice(-2),		// Add leading 0.
    ampm = '',
    time;
    time = dd + '.' + mm;
    return time;
}
function convertTimestampToLocalTime(timestamp) {
    timestamp = parseInt(timestamp);
    var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
    yyyy = d.getFullYear(),
    mm = ('0' + (d.getMonth() + 1)).slice(-2),	// Months are zero based. Add leading 0.
    dd = ('0' + d.getDate()).slice(-2),			// Add leading 0.
    hh = d.getHours(),
    h = hh,
    min = ('0' + d.getMinutes()).slice(-2),		// Add leading 0.
    ampm = '',
    time;

    if (['en', 'en-US'].indexOf(navigator.language) >= 0) {
        // ie: 02/18/2013, 8:35
        time = mm + '/' + dd + '/' + yyyy + ', ' + h + ':' + min + ampm;;
    } else if(['de', 'de-DE'].indexOf(navigator.language) >= 0) {
        // ie: 18.02.2013, 8.35
        time = dd + '.' + mm + '.' + yyyy + ', ' + h + '.' + min + ampm;;
    } else if(['fr', 'fr-FR'].indexOf(navigator.language) >= 0) {
        // ie: 18/02/2013, 8:35
        time = dd + '/' + mm + '/' + yyyy + ', ' + h + ':' + min + ampm;;
    } else if(['jp', 'jp-JP'].indexOf(navigator.language) >= 0) {
        // ie: 2013年02月18日, 8:35
        time = yyyy + '年' + mm + '月' + dd +'日' + ', ' + h + ':' + min + ampm;
    } else {
        // ie: 2013-02-18, 8:35
        time = yyyy + '-' + mm + '-' + dd + ', ' + h + ':' + min + ampm;
    }
    
    return time;
}

function convertTimestampToLocalH_M(timestamp) {
    timestamp = parseInt(timestamp);
    console.log(timestamp);
    var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
    yyyy = d.getFullYear(),
    mm = ('0' + (d.getMonth() + 1)).slice(-2),	// Months are zero based. Add leading 0.
    dd = ('0' + d.getDate()).slice(-2),			// Add leading 0.
    hh = d.getHours(),
    h = hh,
    min = ('0' + d.getMinutes()).slice(-2),		// Add leading 0.
    ampm = '',
    time;

    if (['en', 'en-US'].indexOf(navigator.language) >= 0) {
        // 8:35
        time = h + ':' + min + ampm;;
    } else {
        // 8:35
        time = h + ':' + min + ampm;
    }
    
    return time;
}

function convertTimestampToWeekDay(timestamp) {
    timestamp = parseInt(timestamp);
    var d = new Date(timestamp * 1000),	// Convert the passed timestamp to milliseconds
    
    day = d.getDay();

    if (day === 0) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['sunday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['sunday']}}{% endif %}"
    } else if(day === 1) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['monday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['monday']}}{% endif %}"
    } else if(day === 2) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['tuesday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['tuesday']}}{% endif %}"
    } else if(day === 3) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['wednesday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['wednesday']}}{% endif %}"
    } else if(day === 4) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['thursday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['thursday']}}{% endif %}"
    } else if(day === 5) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['friday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['friday']}}{% endif %}"
    } else if(day === 6) {
        day = "{% if 'language' in session %}{{info['language']['timestamp'][session['language']]['saturday']}}{% else %}{{info['language']['timestamp'][info['defaultlanguage']]['saturday']}}{% endif %}"
    }
    
    return day;
}