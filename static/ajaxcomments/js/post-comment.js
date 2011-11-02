$(document).ready(function() {
    previewed = false;
    
    commentBusy = false;
});

function ajaxComment(args) {
    // TODO: if the media variable ends in a forward slash, remove it.
    var media = args.media;
    
    $('div.comment-error').remove();
    
    if (commentBusy) {
        $('div.comment-form form').before('\
            <div class="comment-error">\
                Your comment is currently in the process of posting.\
            </div>\
        ');
        $('div.comment-error').fadeOut(2000);
        
        return false;
    }
    
    comment = $('div.comment-form form').serialize();
   
    // Add a wait animation
    $('input.submit-post').after('\
        <img src="' + media + '/img/ajax-wait.gif" alt="Please wait..."\
            class="ajax-loader" />\
    ');
    
    // Indicate that the comment is being posted
    $('p.submit').after('\
        <div class="comment-waiting" style="display: none;">\
            One moment while the comment is posted. . .\
        </div>\
    ');
    $('div.comment-waiting').fadeIn(1000);
    
    commentBusy = true;
    
    url = $('div.comment-form form').attr('action');
    
    // Use AJAX to post the comment.
    $.ajax({
        type: 'POST',
        url: url,
        data: comment,
        success: function(data) {
            commentBusy = false;
        
            removeWaitAnimation()
        
            if (data.success == true) {
                commentSuccess(data);
            } else {
                commentFailure(data);
            }
        },
        error: function(data) {
            commentBusy = false;
            
            removeWaitAnimation()
            $('div.comment-form form').unbind('submit');
            $('div.comment-form form').submit();
        },
        dataType: 'json'
    });
    
    return false;
}

function commentSuccess(data) {
    email = $('#id_email').val();
    comment = $('#id_comment').val();
    name = $('#id_name').val();
    url = $('#id_url').val();
/*    
    // Create an MD5 hash from the email address to use with Gravatar
    gravatar = 'http://www.gravatar.com/avatar.php' +
        '?default=&size=48&gravatar_id=' + $.md5(email);
    
    if ($('div#comments').children().length == 0) {
        $('div#comments').prepend(
            '<h2 class="comment-hd">1 comment so far:</h2>'
        )
    }
    
    comment_html = '\
        <div class="comment" style="display: none;">\
            <div class="comment-body">\
                <a href="http://www.gravatar.com">\
                    <img src="' + gravatar + '" /></a>\
                <p>' + comment + '</p>\
            </div>\
        <div class="clear"></div>\
        <p class="posted-by">Posted by <a href="' + url + '">' + 
            name + '</a> 0 minutes ago.</p></div>\
    ';
*/    
    comment_html = '<li class="comment">\
      <span class="comment_name">'+name+'</span> - <span class="comment_date">Just now</span>\
        <p>'+comment+'</p></li>';
      
    $('#id_comment').val('');
    
    $('#comments').append(comment_html);
    $('div.comment:last').show('slow');
    
    $('ul#comments').after('\
        <div class="messages comment-thanks">\
            <ul><li class="success">Thank you for your comment!</li></ul>\
        </div>\
    ');
    $('div.comment-thanks').delay(5000).fadeOut(2000).slideUp(2000);
}

function commentFailure(data) {
    for (var error in data.errors) {
        $('#id_' + error).parent().before(data.errors[error])
    }
}

function removeWaitAnimation() {
    // Remove the wait animation and message
    $('.ajax-loader').remove();
    $('div.comment-waiting').stop().remove();
}