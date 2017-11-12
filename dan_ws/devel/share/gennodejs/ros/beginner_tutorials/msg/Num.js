// Auto-generated. Do not edit!

// (in-package beginner_tutorials.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class Num {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.Amr = null;
    }
    else {
      if (initObj.hasOwnProperty('Amr')) {
        this.Amr = initObj.Amr
      }
      else {
        this.Amr = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Num
    // Serialize message field [Amr]
    bufferOffset = _serializer.string(obj.Amr, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Num
    let len;
    let data = new Num(null);
    // Deserialize message field [Amr]
    data.Amr = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += object.Amr.length;
    return length + 4;
  }

  static datatype() {
    // Returns string type for a message object
    return 'beginner_tutorials/Num';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '41627bb8959d7ae85c352700984f35cc';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string Amr
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Num(null);
    if (msg.Amr !== undefined) {
      resolved.Amr = msg.Amr;
    }
    else {
      resolved.Amr = ''
    }

    return resolved;
    }
};

module.exports = Num;
