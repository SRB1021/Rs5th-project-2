const CANDIDATE_MIME_TYPES = [
  "audio/mp4",
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/ogg;codecs=opus",
];

function pickMimeType() {
  if (typeof MediaRecorder === "undefined") return "";
  return CANDIDATE_MIME_TYPES.find((t) => MediaRecorder.isTypeSupported?.(t)) || "";
}

export function isRecordingSupported() {
  return (
    typeof window !== "undefined" &&
    !!navigator.mediaDevices?.getUserMedia &&
    typeof MediaRecorder !== "undefined"
  );
}

// Creates a push-to-talk recorder backed by a single reusable microphone
// stream (so the permission prompt only happens once per call).
export function createRecorder() {
  let stream = null;
  let recorder = null;
  let chunks = [];

  async function ensureStream() {
    if (!stream) {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }
    return stream;
  }

  async function start() {
    await ensureStream();
    chunks = [];
    const mimeType = pickMimeType();
    recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    recorder.start();
  }

  function stop() {
    return new Promise((resolve, reject) => {
      if (!recorder) {
        reject(new Error("Recording was never started"));
        return;
      }
      recorder.onstop = () => resolve(new Blob(chunks, { type: recorder.mimeType || "audio/webm" }));
      recorder.onerror = (e) => reject(e.error || new Error("Recording failed"));
      recorder.stop();
    });
  }

  function release() {
    stream?.getTracks().forEach((t) => t.stop());
    stream = null;
    recorder = null;
    chunks = [];
  }

  return { start, stop, release, requestPermission: ensureStream };
}
