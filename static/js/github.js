var prov = new firebase.auth.GithubAuthProvider();
var auth = firebase.auth();

$('#g_login').click(function() {
    auth.signInWithPopup(prov).then(function(result) {
        var tok = result.credential.accessToken;
        var user = result.user;

        console.log(JSON.stringify(user));
        var uid = user.uid;
        var name = user.providerData[0].displayName;
        if (name == null) { name = user.providerData[0].uid; }

        $.cookie('uid', uid);
        $.cookie('dname', name);
        $.cookie('edate', user.stsTokenManager.expirationTime);
    }).catch(function(error) {
        var errorCode = error.code;
        var errorMsg = error.message;

        console.log(errorCode + ': ' + errorMsg);
    });
});

function epochNow() {}
    
}

if ($.cookie('edate'))