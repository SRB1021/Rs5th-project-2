const MESSAGES_KEY = "textmate.messages";
const PERSONA_KEY = "textmate.persona";

export function loadMessages() {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(MESSAGES_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveMessages(messages) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages.slice(-200)));
  } catch {
    // ignore quota errors
  }
}

export function loadPersona(defaultPersona) {
  if (typeof window === "undefined") return defaultPersona;
  try {
    const raw = window.localStorage.getItem(PERSONA_KEY);
    return raw ? JSON.parse(raw) : defaultPersona;
  } catch {
    return defaultPersona;
  }
}

export function savePersona(persona) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(PERSONA_KEY, JSON.stringify(persona));
  } catch {
    // ignore
  }
}
