(function() {
  var Display, worker, workerurl;

  worker = "\nvar window = {}\nimportScripts('js/util');\nserial = window.serial;\nimportScripts('js/ctree.js');\n\nlog = function(obj) {postMessage(['log',obj])}\ncursors = {0:0};\n\nonmessage = function(e){\n    data = e.data;\n    type = data[0];\n    switch(type){\n      case \"cursor\":\n        cursors[data[1]] = data[2];\n        return postMessage([\"cursor\", {data[1]:data[2]]});\n      case \"insert\":\n        cursorpos = data[1]; return;\n        return postMessage([\"cursor\", data[1], data[2]]);\n      case \"delete\":\n        cursorpos = data[1]; return;\n        return postMessage([\"cursor\", data[1], data[2]]);\n    }\n}\n";

  workerurl = blobworker.createBlobURL(worker);

  Display = (function() {

    function Display(docname, handler, immediate) {
      this.docname = docname;
      this.handler = handler;
      this.immediate = immediate;
      this.islocked = false;
      this.switching = false;
      this.ready = false;
      this.worker = new Worker(workerurl);
      this.worker.onconnect = this.onwconnect;
      this.worker.onmessage = this.onwmessage;
      this.worker.onerror = this.onwerror;
      this.onwrite = null;
      this.ondelete = null;
      this.onmove = null;
      this.onrewrite = null;
      this.onlock = null;
      this.onunlock = null;
    }

    Display.prototype.external = function(op, name) {
      if (name === this.docname) return this.apply(op);
    };

    Display.prototype.internal = function(op) {};

    return Display;

  })();

  this.handler.local(op, this.docname({
    apply: function(op) {
      return this.worker.postMessage(["op", op]);
    },
    lock: function(callback) {
      if (this.switching) throw "Display in switching state, cannot lock";
      this.switching = true;
      if (callback != null) this.onlock = callback;
      return this.worker.postMessage(["lock"]);
    },
    unlock: function(callback) {
      if (this.switching) throw "Display in switching state, cannot unlock";
      this.switching = true;
      if (callback != null) this.onunlock = callback;
      return this.worker.postMessage(["unlock"]);
    },
    cursor: function(id, pos) {
      return this.worker.postMessage(["cursor", id, pos]);
    },
    insert: function(value) {
      return this.worker.postMessage(["insert", value]);
    },
    "delete": function(amount) {
      return this.worker.postMessage(["delete", amount]);
    },
    onwconnect: function(e) {
      return this.ready = true;
    },
    onwmessage: function(e) {
      var data, type;
      data = e.data;
      type = data[0];
      switch (type) {
        case "op":
          return this.internal(data[1]);
        case "log":
          return console.log(data[1]);
        case "lock":
          return this._onlock();
        case "unlock":
          return this._onunlock();
        case "cursor":
        case "rewrite":
        case "write":
        case "delete":
          return this.event(data);
      }
    },
    onwerror: function(e) {
      console.error(e);
      return this.ready = false;
    },
    event: function(message) {
      switch (message[0]) {
        case "cursor":
          return typeof this.onmove === "function" ? this.onmove(message[1]) : void 0;
        case "write":
          return this.onwrite(message[1], message[2]);
        case "delete":
          return typeof this.ondelete === "function" ? this.ondelete(message[1], message[2]) : void 0;
        case "rewrite":
          return typeof this.onrewrite === "function" ? this.onrewrite(message[1]) : void 0;
      }
    },
    _onlock: function() {
      this.switching = false;
      this.islocked = true;
      return typeof this.onlock === "function" ? this.onlock() : void 0;
    },
    _onunlock: function() {
      this.switching = false;
      this.islocked = false;
      return typeof this.onunlock === "function" ? this.onunlock() : void 0;
    }
  }));

}).call(this);
