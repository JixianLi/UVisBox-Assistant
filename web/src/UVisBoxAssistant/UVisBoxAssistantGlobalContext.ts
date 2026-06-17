// ABOUTME: Global context for the UVisBoxAssistant scenario — MobX store backed by a WebSocket client.
// ABOUTME: Translates server envelopes (session_ready/trace/chat/busy/error) into observable state.

import { makeAutoObservable, runInAction } from "mobx";
import type { GlobalContext } from "@/Types/GlobalContext";
import type { Actor, TraceMessage } from "@/Renderers/Trace";
import type { ChatMessage } from "@/Renderers/Chat";

type ConnectionState = "connecting" | "connected" | "disconnected";

export class UVisBoxAssistantGlobalContext implements GlobalContext {
    actors: Actor[];
    traceMessages: TraceMessage[];
    chatMessages: ChatMessage[];
    selectedTraceId: string | null;
    busy: boolean;
    connectionState: ConnectionState;
    chatFontSize: number;
    traceFontSize: number;

    private ws: WebSocket | null;

    constructor() {
        this.actors = [];
        this.traceMessages = [];
        this.chatMessages = [];
        this.selectedTraceId = null;
        this.busy = false;
        this.connectionState = "disconnected";
        this.chatFontSize = 14;
        this.traceFontSize = 13;
        this.ws = null;

        makeAutoObservable<this, "ws">(this, { ws: false });

        this.appendTrace = this.appendTrace.bind(this);
        this.appendChat = this.appendChat.bind(this);
        this.selectTrace = this.selectTrace.bind(this);
        this.submitUserPrompt = this.submitUserPrompt.bind(this);
        this.reset = this.reset.bind(this);
        this.setChatFontSize = this.setChatFontSize.bind(this);
        this.setTraceFontSize = this.setTraceFontSize.bind(this);
    }

    setChatFontSize(px: number) {
        this.chatFontSize = px;
    }

    setTraceFontSize(px: number) {
        this.traceFontSize = px;
    }

    appendTrace(msg: TraceMessage) {
        this.traceMessages.push(msg);
    }

    appendChat(msg: ChatMessage) {
        this.chatMessages.push(msg);
    }

    selectTrace(id: string | null) {
        this.selectedTraceId = id;
    }

    submitUserPrompt(text: string) {
        if (this.busy || this.connectionState !== "connected" || !this.ws) return;
        this.ws.send(JSON.stringify({ type: "prompt", text }));
    }

    reset() {
        if (this.connectionState !== "connected" || !this.ws) return;
        this.ws.send(JSON.stringify({ type: "reset" }));
    }

    initialize(globalData: any): void {
        if (typeof globalData?.chat_font_size === "number") {
            this.chatFontSize = globalData.chat_font_size;
        }
        if (typeof globalData?.trace_font_size === "number") {
            this.traceFontSize = globalData.trace_font_size;
        }
    }

    async asyncInitialize(): Promise<void> {
        this.connect();
    }

    private connect() {
        runInAction(() => {
            this.connectionState = "connecting";
        });

        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        const url = `${proto}//${window.location.host}/ws`;
        const ws = new WebSocket(url);
        this.ws = ws;

        ws.onopen = () => {
            runInAction(() => {
                this.connectionState = "connected";
            });
            ws.send(JSON.stringify({ type: "hello" }));
        };

        ws.onmessage = (ev) => {
            let parsed: any;
            try {
                parsed = JSON.parse(ev.data);
            } catch (err) {
                console.warn("Failed to parse server message", err, ev.data);
                return;
            }
            this.handleServerMessage(parsed);
        };

        ws.onclose = () => {
            runInAction(() => {
                this.connectionState = "disconnected";
                this.appendChat({
                    id: crypto.randomUUID(),
                    role: "system",
                    content: "Disconnected from server. Reload the page to reconnect.",
                });
            });
        };

        ws.onerror = (err) => {
            console.error("WebSocket error", err);
        };
    }

    private handleServerMessage(msg: any) {
        switch (msg.type) {
            case "session_ready":
                runInAction(() => {
                    this.actors = msg.actors ?? [];
                    this.traceMessages = [];
                    this.chatMessages = [];
                    this.selectedTraceId = null;
                });
                return;
            case "trace":
                runInAction(() => {
                    this.appendTrace(msg.message as TraceMessage);
                });
                return;
            case "chat":
                runInAction(() => {
                    this.appendChat(msg.message as ChatMessage);
                });
                return;
            case "busy":
                runInAction(() => {
                    this.busy = Boolean(msg.busy);
                });
                return;
            case "error":
                runInAction(() => {
                    this.appendChat({
                        id: crypto.randomUUID(),
                        role: "system",
                        content: String(msg.message ?? "Unknown server error"),
                    });
                });
                return;
            default:
                console.warn("Unknown server message type", msg);
                return;
        }
    }

    toObject(): any {
        return {
            actors: this.actors,
            trace_messages: this.traceMessages,
            chat_messages: this.chatMessages,
        };
    }
}

export default UVisBoxAssistantGlobalContext;
