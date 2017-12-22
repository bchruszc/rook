var db = new Dexie('test_data3');
db.version(1).stores({
  games: 'id,entered_date,played_date,scores,bids',
  bids: 'id,caller,partners,opponents,points_bid,points_made',
  scores: 'id,player,rank,score,made_bid',
  players: 'id,player_id,first_name,last_name'
});


db.on('ready', function () {
    db.games = [];
    db.bids = [];
    db.scores = [];
    db.players = [];
}


// Populate from AJAX:
db.on('ready', function () {
    // on('ready') event will fire when database is open but
    // before any other queued operations start executing.
    // By returning a Promise from this event,
    // the framework will wait until promise completes before
    // resuming any queued database operations.
    // Let's start by using the count() method to detect if
    // database has already been populated.

    // TODO:  A date related scheme to reload just the latest games?

    return db.games.count(function (count) {
        if (count > 0) {
            console.log("Games already populated");
        } else {
            console.log("Games database is empty. Populating from ajax call...");
            // We want framework to continue waiting, so we encapsulate
            // the ajax call in a Dexie.Promise that we return here.
            return new Dexie.Promise(function (resolve, reject) {
                $.ajax('/raw/games/', {
                    type: 'get',
                    dataType: 'json',
                    error: function (xhr, textStatus) {
                        // Rejecting promise to make db.open() fail.
                        reject(textStatus);
                    },
                    success: function (data) {
                        // Resolving Promise will launch then() below.
                        resolve(data);
                    }
                });
            }).then(function (data) {
                console.log("Got ajax response. We'll now add the objects.");
                // By returning the db.transaction() promise, framework will keep
                // waiting for this transaction to commit before resuming other
                // db-operations.
                return db.transaction('rw', db.games, function () {
                    data.forEach(function (item) {
                        //console.log("Adding object: " + JSON.stringify(item));
                        db.games.add(item);
                    });
                });
            }).then(function () {
                console.log ("Transaction committed");
            });
        }
    });
});

// Scores
// Populate from AJAX:
db.on('ready', function () {
    // on('ready') event will fire when database is open but
    // before any other queued operations start executing.
    // By returning a Promise from this event,
    // the framework will wait until promise completes before
    // resuming any queued database operations.
    // Let's start by using the count() method to detect if
    // database has already been populated.

    // TODO:  A date related scheme to reload just the latest games?

    return db.scores.count(function (count) {
        if (count > 0) {
            console.log("Scores already populated");
        } else {
            console.log("Scores database is empty. Populating from ajax call...");
            // We want framework to continue waiting, so we encapsulate
            // the ajax call in a Dexie.Promise that we return here.
            return new Dexie.Promise(function (resolve, reject) {
                $.ajax('/raw/scores/', {
                    type: 'get',
                    dataType: 'json',
                    error: function (xhr, textStatus) {
                        // Rejecting promise to make db.open() fail.
                        reject(textStatus);
                    },
                    success: function (data) {
                        // Resolving Promise will launch then() below.
                        resolve(data);
                    }
                });
            }).then(function (data) {
                console.log("Got ajax response. We'll now add the objects.");
                // By returning the db.transaction() promise, framework will keep
                // waiting for this transaction to commit before resuming other
                // db-operations.
                return db.transaction('rw', db.scores, function () {
                    data.forEach(function (item) {
                        //console.log("Adding object: " + JSON.stringify(item));
                        db.scores.add(item);
                    });
                });
            }).then(function () {
                console.log ("Transaction committed");
            });
        }
    });
});

// Bids
// Populate from AJAX:
db.on('ready', function () {
    // on('ready') event will fire when database is open but
    // before any other queued operations start executing.
    // By returning a Promise from this event,
    // the framework will wait until promise completes before
    // resuming any queued database operations.
    // Let's start by using the count() method to detect if
    // database has already been populated.

    // TODO:  A date related scheme to reload just the latest games?

    return db.bids.count(function (count) {
        if (count > 0) {
            console.log("Bids already populated");
        } else {
            console.log("Bids database is empty. Populating from ajax call...");
            // We want framework to continue waiting, so we encapsulate
            // the ajax call in a Dexie.Promise that we return here.
            return new Dexie.Promise(function (resolve, reject) {
                $.ajax('/raw/bids/', {
                    type: 'get',
                    dataType: 'json',
                    error: function (xhr, textStatus) {
                        // Rejecting promise to make db.open() fail.
                        reject(textStatus);
                    },
                    success: function (data) {
                        // Resolving Promise will launch then() below.
                        resolve(data);
                    }
                });
            }).then(function (data) {
                console.log("Got ajax response. We'll now add the objects.");
                // By returning the db.transaction() promise, framework will keep
                // waiting for this transaction to commit before resuming other
                // db-operations.
                return db.transaction('rw', db.bids, function () {
                    data.forEach(function (item) {
                        //console.log("Adding object: " + JSON.stringify(item));
                        db.bids.add(item);
                    });
                });
            }).then(function () {
                console.log ("Transaction committed");
            });
        }
    });
});

//Players
// Populate from AJAX:
db.on('ready', function () {
    // on('ready') event will fire when database is open but
    // before any other queued operations start executing.
    // By returning a Promise from this event,
    // the framework will wait until promise completes before
    // resuming any queued database operations.
    // Let's start by using the count() method to detect if
    // database has already been populated.

    // TODO:  A date related scheme to reload just the latest games?

    return db.players.count(function (count) {
        if (count > 0) {
            console.log("Playres already populated");
        } else {
            console.log("Players database is empty. Populating from ajax call...");
            // We want framework to continue waiting, so we encapsulate
            // the ajax call in a Dexie.Promise that we return here.
            return new Dexie.Promise(function (resolve, reject) {
                $.ajax('/raw/players/', {
                    type: 'get',
                    dataType: 'json',
                    error: function (xhr, textStatus) {
                        // Rejecting promise to make db.open() fail.
                        reject(textStatus);
                    },
                    success: function (data) {
                        // Resolving Promise will launch then() below.
                        resolve(data);
                    }
                });
            }).then(function (data) {
                console.log("Got ajax response. We'll now add the objects.");
                // By returning the db.transaction() promise, framework will keep
                // waiting for this transaction to commit before resuming other
                // db-operations.
                return db.transaction('rw', db.players, function () {
                    data.forEach(function (item) {
                        //console.log("Adding object: " + JSON.stringify(item));
                        db.players.add(item);
                    });
                });
            }).then(function () {
                console.log ("Transaction committed");
            });
        }
    });
});


db.open(); // Will resolve when data is fully populated (or fail if error)

// Example - find the game with the latest played date
db.games
.orderBy("played_date")
.reverse()
.limit(1)
.toArray()
.then(function(sessions) {
    console.log (
        "Last game: " +
        sessions.map(function (s) { return s.played_date }));
});