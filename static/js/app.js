function floatTo16BitPCM(output, offset, input) {
    for (var i = 0; i < input.length; i++, offset += 2) {
        var s = Math.max(-1, Math.min(1, input[i]));
        output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
}

function writeString(view, offset, string) {
    for (var i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

function interleave(a, b) {
    var len = a.length + b.length;
    var result = new Float32Array(len);
    var index = 0;
    var inputIndex = 0;

    while (index < len) {
        result[index++] = a[inputIndex];
        result[index++] = b[inputIndex];
        inputIndex++;
    }

    return result;
}

function encodeWAV(samples, sampleRate, numChannels) {
    var buffer = new ArrayBuffer(44 + samples.length * 2);
    var view = new DataView(buffer);
    /* RIFF identifier */
    writeString(view, 0, 'RIFF');
    /* file length */
    view.setUint32(4, 36 + samples.length * 2, true);
    /* RIFF type */
    writeString(view, 8, 'WAVE');
    /* format chunk identifier */
    writeString(view, 12, 'fmt ');
    /* format chunk length */
    view.setUint32(16, 16, true);
    /* sample format (raw) */
    view.setUint16(20, 1, true);
    /* channel count */
    view.setUint16(22, numChannels, true);
    /* sample rate */
    view.setUint32(24, sampleRate, true);
    /* byte rate (sample rate * block align) */
    view.setUint32(28, sampleRate * 4, true);
    /* block align (channel count * bytes per sample) */
    view.setUint16(32, numChannels * 2, true);
    /* bits per sample */
    view.setUint16(34, 16, true);
    /* data chunk identifier */
    writeString(view, 36, 'data');
    /* data chunk length */
    view.setUint32(40, samples.length * 2, true);
    floatTo16BitPCM(view, 44, samples);
    return view;
}

function mergeBuffers(buffers, len) {
    var result = new Float32Array(len);
    var offset = 0;
    for (var i = 0; i < buffers.length; i++) {
        result.set(buffers[i], offset);
        offset += buffers[i].length;
    }
    return result;
}

function exportWAV(record, context) {
    var numChannels = record.buffers.length;
    var buffers = [];
    for (var i = 0; i < numChannels; i++) {
        buffers.push(mergeBuffers(record.buffers[i], record.length));
    }
    var interleaved = numChannels == 2 ? interleave(buffers[0], buffers[1]) : buffers[0];
    var dataView = encodeWAV(interleaved, context.sampleRate, numChannels);
    var blob = new Blob([dataView], {type: 'audio/wav'});
    blob.name = Math.floor((new Date()).getTime() / 1000) + '.wav';
    return blob;
}

function stopAudioOnly(stream) {
    stream.getTracks().forEach(function (track) {
        if (track.readyState == 'live' && track.kind === 'audio') {
            track.stop();
        }
    });
}

function makeRecoder() {
    var numChannels = 2;
    var context = null;
    var currentStream = null;

    var listening = false;
    var initialized = false;

    function makeRecord() {
        return {
            length: 0,
            buffers: [[], []]
        }
    }

    function nop () {}

    var record = makeRecord();
    var closeAudio = nop;

    function initAudio() {
        var source = null;
        var node = null;
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
            currentStream = stream;
            var audioContext = new AudioContext();
            source = audioContext.createMediaStreamSource(stream);
            context = source.context;
            var createNodeMethod = (
                context.createScriptProcessor ||
                context.createJavaScriptNode
            );
            node = createNodeMethod.call(context, 4096, numChannels, numChannels);
            node.onaudioprocess = function (e) {
                if (!listening) return;
                for (var i = 0; i < numChannels; i++) {
                    record.buffers[i].push(
                    [...e.inputBuffer.getChannelData(i)]);
                }
                record.length += record.buffers[0][0].length;
            }
            source.connect(node);
            node.connect(context.destination);
        });

        return function() {
            node.disconnect();
            source.disconnect();
        }
    }

    return {
        data: null,
        listening: false,
        start: function () {
            console.log('start listening')
            this.listening = listening = true;
            this.date = null;
            if (!initialized) {
                initialized = true;
                closeAudio = initAudio();
            }
        },
        stop: function () {
            console.log('stop listening');
            stopAudioOnly(currentStream);
            initialized = false;
            closeAudio();
            closeAudio = nop;
            this.listening = listening = false;
            this.data = exportWAV(record, context);
            record = makeRecord();
        }
    }
}

function createAudioPlayer(audioBlob) {
    var audioUrl = URL.createObjectURL(audioBlob);
    var audio = new Audio(audioUrl);
    return function () {
        return audio.play();
    }
}

function uploadAudioBlob(url, audio, successUrl) {
    var formData = new FormData();
    formData.append('audio_file', audio, 'audio.wav')
    $.ajax({
        type: "POST",
        url: url,
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            location.replace(successUrl);
        },
        error: function (xhr, status, error) {
            alert("Nieodebrano poprawnie.");
            console.log(status, error);
        }
    })
}

function innerMessage(message) {
    var box = document.getElementById("message");
    const externalHTML = '<div style="position: absolute; width: 98%; z-index: 1;">\n' +
        '    <div class="alert alert-danger alert-dismissible messages shadow p-3 mb-5 bg-body rounded" style="display: none; opacity: 0.9" role="alert">\n' + message + '</div>\n' + '</div>';

    setTimeout(function () {
        $('.messages').fadeIn('fast');
    }, 1);
    box.innerHTML = externalHTML;
    setTimeout(function () {
        $('.messages').fadeOut('fast');
    }, 3000);

}

function setupButtons(successUrl) {
    var $recordButton = $('#recordButton');
    var recoder = makeRecoder();
    $('#recAnimation').addClass("notRec");
    $recordButton.click(function () {
        if ($('#recAnimation').hasClass('notRec')) {
            $('#recAnimation').removeClass("notRec");
            $('#recAnimation').addClass("Rec");
            $('#recText').fadeIn('slow');
            // document.getElementById('recText').style.display = 'inline-block';
        } else {
            $('#recAnimation').removeClass("Rec");
            $('#recAnimation').addClass("notRec");
            $('#recText').fadeOut('slow');
            //document.getElementById('recText').style.display = 'none';
        }
        if (recoder.listening) {
            $recordButton.text('Nagraj');
            recoder.stop();
        } else {
            $recordButton.text('Stop');
            recoder.start();
        }
    });

    var $playButton = $('#playButton');
    $playButton.click(function () {
        if (recoder.data === null) {
            //   alert("Nagraj dźwięk przed odtworzeniem.");
            innerMessage("Nagraj dźwięk przed odtworzeniem.");
            return;
        }

        var audioUrl = URL.createObjectURL(recoder.data);
        var audio = new Audio(audioUrl);
        audio.play();
    });

    var $uploadButton = $("#uploadButton");
    var uploadAudioUrl = $uploadButton.data("upload-url");
    $uploadButton.click(function () {
        if (recoder.data === null) {
            //alert("Nagraj dźwięk przed przesłaniem.");
            innerMessage("Nagraj dźwięk przed przesłaniem.")
            return;
        }
        uploadAudioBlob(uploadAudioUrl, recoder.data, successUrl);
    });

}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function setupAjax(csrfToken) {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });
}


$(function () {
    setupButtons(SUCCESS_URL);
    setupAjax(CSRF_TOKEN);
});

