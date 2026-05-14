// ABOUTME: Vitest unit tests for UVisBoxAssistantGlobalContext WebSocket state machine.
// ABOUTME: Stubs the global WebSocket with a capture mock and drives lifecycle/message events.

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { configure, runInAction } from "mobx";
import { UVisBoxAssistantGlobalContext } from "../UVisBoxAssistantGlobalContext";

configure({ enforceActions: "never" });

class MockWebSocket {
    static instances: MockWebSocket[] = [];
    static CONNECTING = 0;
    static OPEN = 1;
    static CLOSING = 2;
    static CLOSED = 3;

    readyState: number = MockWebSocket.CONNECTING;
    url: string;
    sent: string[] = [];
    onopen: ((ev: Event) => void) | null = null;
    onmessage: ((ev: MessageEvent) => void) | null = null;
    onclose: ((ev: CloseEvent) => void) | null = null;
    onerror: ((ev: Event) => void) | null = null;

    constructor(url: string) {
        this.url = url;
        MockWebSocket.instances.push(this);
    }

    send(data: string) {
        this.sent.push(data);
    }

    close() {
        this.readyState = MockWebSocket.CLOSED;
        this.onclose?.(new CloseEvent("close"));
    }

    simulateOpen() {
        this.readyState = MockWebSocket.OPEN;
        this.onopen?.(new Event("open"));
    }

    simulateMessage(payload: unknown) {
        this.onmessage?.(new MessageEvent("message", { data: JSON.stringify(payload) }));
    }

    simulateClose() {
        this.readyState = MockWebSocket.CLOSED;
        this.onclose?.(new CloseEvent("close"));
    }
}

async function flushMicrotasks() {
    await Promise.resolve();
    await Promise.resolve();
}

async function makeContext(): Promise<{
    ctx: UVisBoxAssistantGlobalContext;
    socket: MockWebSocket;
}> {
    const ctx = new UVisBoxAssistantGlobalContext();
    await ctx.asyncInitialize();
    await flushMicrotasks();
    const socket = MockWebSocket.instances[0];
    return { ctx, socket };
}

function sessionReadyPayload() {
    return {
        type: "session_ready",
        actors: [
            { id: "user", label: "User", kind: "user" },
            { id: "model", label: "Model", kind: "model" },
            { id: "data_tool", label: "Data Tool", kind: "tool" },
            { id: "vis_tool", label: "Vis Tool", kind: "tool" },
        ],
    };
}

describe("UVisBoxAssistantGlobalContext", () => {
    beforeEach(() => {
        MockWebSocket.instances = [];
        vi.stubGlobal("WebSocket", MockWebSocket);
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it("sends hello on open", async () => {
        const { ctx, socket } = await makeContext();

        socket.simulateOpen();

        expect(socket.sent.length).toBe(1);
        expect(JSON.parse(socket.sent[0])).toEqual({ type: "hello" });
        expect(ctx.connectionState).toBe("connected");
    });

    it("session_ready replaces actors and clears stores", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();

        runInAction(() => {
            ctx.traceMessages.push({
                id: "pre-trace",
                from: "user",
                to: "model",
                payload: "pre-existing",
            });
            ctx.chatMessages.push({
                id: "pre-chat",
                role: "user",
                content: "pre-existing",
            });
        });
        expect(ctx.traceMessages.length).toBe(1);
        expect(ctx.chatMessages.length).toBe(1);

        socket.simulateMessage(sessionReadyPayload());

        expect(ctx.traceMessages.length).toBe(0);
        expect(ctx.chatMessages.length).toBe(0);
        expect(ctx.actors.length).toBe(4);
        expect(ctx.actors.map((a) => a.id)).toEqual([
            "user",
            "model",
            "data_tool",
            "vis_tool",
        ]);
    });

    it("trace message gets appended", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        const traceMsg = {
            id: "t1",
            from: "user",
            to: "model",
            kind: "prompt",
            payload: "hello",
        };
        socket.simulateMessage({ type: "trace", message: traceMsg });

        expect(ctx.traceMessages.length).toBe(1);
        expect(ctx.traceMessages[0]).toEqual(traceMsg);
    });

    it("chat message with image content preserves content parts", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        const chatMsg = {
            id: "c1",
            role: "assistant",
            authorName: "Vis Tool",
            content: [
                { type: "text", text: "Boxplot done." },
                { type: "image", url: "/figures/abc.png", alt: "functional_boxplot" },
            ],
        };
        socket.simulateMessage({ type: "chat", message: chatMsg });

        expect(ctx.chatMessages.length).toBe(1);
        const entry = ctx.chatMessages[0];
        expect(Array.isArray(entry.content)).toBe(true);
        expect((entry.content as unknown[]).length).toBe(2);
        expect(entry.content).toEqual([
            { type: "text", text: "Boxplot done." },
            { type: "image", url: "/figures/abc.png", alt: "functional_boxplot" },
        ]);
    });

    it("busy:true blocks submitUserPrompt", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        expect(socket.sent.length).toBe(1);

        socket.simulateMessage({ type: "busy", busy: true });
        expect(ctx.busy).toBe(true);

        ctx.submitUserPrompt("hi");

        expect(socket.sent.length).toBe(1);
        expect(JSON.parse(socket.sent[0])).toEqual({ type: "hello" });
    });

    it("submitUserPrompt sends a prompt envelope when connected and not busy", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        ctx.submitUserPrompt("plot something");

        const last = socket.sent[socket.sent.length - 1];
        expect(JSON.parse(last)).toEqual({ type: "prompt", text: "plot something" });
    });

    it("reset sends reset envelope", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        socket.simulateMessage({
            type: "trace",
            message: { id: "t-keep", from: "user", to: "model", payload: "keep" },
        });
        socket.simulateMessage({
            type: "chat",
            message: { id: "c-keep", role: "user", content: "keep" },
        });
        const traceLenBefore = ctx.traceMessages.length;
        const chatLenBefore = ctx.chatMessages.length;

        ctx.reset();

        const last = socket.sent[socket.sent.length - 1];
        expect(JSON.parse(last)).toEqual({ type: "reset" });
        expect(ctx.traceMessages.length).toBe(traceLenBefore);
        expect(ctx.chatMessages.length).toBe(chatLenBefore);
    });

    it("reset followed by session_ready clears stores", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        socket.simulateMessage({
            type: "trace",
            message: { id: "t-stale", from: "user", to: "model", payload: "stale" },
        });
        socket.simulateMessage({
            type: "chat",
            message: { id: "c-stale", role: "user", content: "stale" },
        });
        expect(ctx.traceMessages.length).toBeGreaterThan(0);
        expect(ctx.chatMessages.length).toBeGreaterThan(0);

        ctx.reset();
        socket.simulateMessage(sessionReadyPayload());

        expect(ctx.traceMessages.length).toBe(0);
        expect(ctx.chatMessages.length).toBe(0);
    });

    it("error message appends a system-role chat", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        socket.simulateMessage({ type: "error", message: "something broke" });

        expect(ctx.chatMessages.length).toBe(1);
        const entry = ctx.chatMessages[ctx.chatMessages.length - 1];
        expect(entry.role).toBe("system");
        expect(String(entry.content)).toContain("something broke");
        expect(typeof entry.id).toBe("string");
        expect(entry.id.length).toBeGreaterThan(0);
    });

    it("onclose marks disconnected and appends system chat", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        const chatLenBefore = ctx.chatMessages.length;

        socket.simulateClose();

        expect(ctx.connectionState).toBe("disconnected");
        expect(ctx.chatMessages.length).toBeGreaterThan(chatLenBefore);
        const systemEntries = ctx.chatMessages.filter((m) => m.role === "system");
        expect(systemEntries.length).toBeGreaterThan(0);
        const mentionsDisconnect = systemEntries.some((m) =>
            String(m.content).toLowerCase().includes("disconnect"),
        );
        expect(mentionsDisconnect).toBe(true);
    });

    it("submitUserPrompt is noop when disconnected", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateClose();

        const sentBefore = socket.sent.length;
        ctx.submitUserPrompt("hi");

        expect(socket.sent.length).toBe(sentBefore);
    });

    it("unknown message type is ignored without throw", async () => {
        const { ctx, socket } = await makeContext();
        socket.simulateOpen();
        socket.simulateMessage(sessionReadyPayload());

        const traceLenBefore = ctx.traceMessages.length;
        const chatLenBefore = ctx.chatMessages.length;

        expect(() => {
            socket.simulateMessage({ type: "nonsense", whatever: 1 });
        }).not.toThrow();

        expect(ctx.traceMessages.length).toBe(traceLenBefore);
        expect(ctx.chatMessages.length).toBe(chatLenBefore);
    });
});
