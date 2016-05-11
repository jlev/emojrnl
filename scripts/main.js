$(document).ready(function() {
    var iOS = !!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform);
    if (iOS) { $('html').addClass('ios'); console.log('ios!'); }
});
