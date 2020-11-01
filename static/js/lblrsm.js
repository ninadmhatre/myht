toastr.options = {
  "closeButton": false,
  "debug": false,
  "newestOnTop": true,
  "progressBar": false,
  "positionClass": "toast-bottom-right",
  "preventDuplicates": true,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}

var flashToToaster = function() {
    var $flash = $('ul.flash');

    if ( $flash.length > 0 ) {
        $flash.find('li').each(function() {
            var msgp = $(this).text().split(':');
            var type = msgp[0];
            var msg = msgp[1];
            if ( type == 'info'  ) {
                showInfo(msg);
            } else if ( type == 'error' || type == 'warn' ) {
                showError(msg);
            } else if ( type == 'success') {
                showSuccess(msg);
            }
        });
        $flash.remove();
    }
};

var showInfo = function(msg) { toastr.info(msg); };
var showError = function(msg) { toastr.error(msg); };
var showSuccess = function(msg) { toastr.success(msg); };

var toggleButton = function(btnType, enable) {
    var $btn = $('input[type="' + btnType +'"]');
    if (enable) {
        $btn.attr('disabled', false);
    } else {
        $btn.attr('disabled', true);
    }
};

var enableButton = function(btnType) {
    toggleButton(btnType, true);
};

var disableButton = function(btnType) {
    toggleButton(btnType, false);
};
