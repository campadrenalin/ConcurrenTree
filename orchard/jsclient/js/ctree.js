(function() {
  var CTree, protostr, protoval, window;

  window = this;

  CTree = (function() {

    function CTree(value) {
      this.value = value;
      this.length = value.length;
      this.key = serial.key(value);
      this.deletions = [];
      window.arrayFill(this.deletions, (function() {
        return false;
      }), this.length);
      this.children = [];
      window.arrayFill(this.children, (function() {
        return {};
      }), this.length + 1);
    }

    CTree.prototype.insert = function(pos, childtext) {
      var child;
      child = new CTree(childtext);
      return this.insert_obj(pos(child));
    };

    CTree.prototype["delete"] = function(pos) {
      var x, _ref, _ref2;
      if (window.isArray(pos)) {
        for (x = _ref = pos[0], _ref2 = pos[1]; _ref <= _ref2 ? x <= _ref2 : x >= _ref2; _ref <= _ref2 ? x++ : x--) {
          this["delete"](x);
        }
      } else {
        this.deletions[pos] = true;
      }
      return this;
    };

    CTree.prototype.insert_obj = function(pos, child) {
      this.children[pos][child.key] = child;
      return child;
    };

    CTree.prototype.flatten = function() {
      var node, nodes, p, result, _i, _len, _ref;
      result = "";
      for (p = 0, _ref = this.length; 0 <= _ref ? p <= _ref : p >= _ref; 0 <= _ref ? p++ : p--) {
        nodes = this.kids(p);
        for (_i = 0, _len = nodes.length; _i < _len; _i++) {
          node = nodes[_i];
          result += node.flatten();
        }
        if (p < this.length && !this.deletions[p]) result += this.value[p];
      }
      return result;
    };

    CTree.prototype.get = function(pos, key) {
      return this.children[pos][key];
    };

    CTree.prototype.keys = function(pos) {
      var key;
      return ((function() {
        var _results;
        _results = [];
        for (key in this.children[pos]) {
          _results.push(key);
        }
        return _results;
      }).call(this)).sort();
    };

    CTree.prototype.kids = function(pos) {
      var key, _i, _len, _ref, _results;
      _ref = this.keys(pos);
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        key = _ref[_i];
        _results.push(this.get(pos, key));
      }
      return _results;
    };

    CTree.prototype.jump = function(pos, key) {
      return key(pos === this.length ? void 0 : [pos, key]);
    };

    return CTree;

  })();

  protostr = function(item) {
    if (typeof item === "string") {
      return item;
    } else {
      return "";
    }
  };

  protoval = function(list) {
    var i;
    return ((function() {
      var _i, _len, _results;
      _results = [];
      for (_i = 0, _len = list.length; _i < _len; _i++) {
        i = list[_i];
        _results.push(protostr(i));
      }
      return _results;
    })()).join("");
  };

  this.CTreeFromProto = function(proto) {
    var deletions, i, pos, tree, value, _i, _j, _len, _len2;
    deletions = proto.pop();
    value = protoval(proto);
    tree = new CTree(value);
    for (_i = 0, _len = deletions.length; _i < _len; _i++) {
      i = deletions[_i];
      tree["delete"](i);
    }
    pos = 0;
    for (_j = 0, _len2 = proto.length; _j < _len2; _j++) {
      i = proto[_j];
      if (typeof i === "string") {
        pos += i.length;
      } else {
        tree.insert_obj(pos, window.CTreeFromProto(i));
      }
    }
    return tree;
  };

  this.CTree = CTree;

}).call(this);
