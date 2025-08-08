import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const GLOSSARY_COLOR = "#14b8a6"; // teal-500

function getSessionId() {
  let id = sessionStorage.getItem("nl2sql_session");
  if (!id) {
    id = crypto.randomUUID();     
    sessionStorage.setItem("nl2sql_session", id);
  }
  return id;
}


function SideGlossary({ open, toggle }) {
  const arrow = open ? "→" : "←";
  return (
    <>
      <button className="glossary-toggle" onClick={toggle} title="Prompt glossary">{arrow}</button>

      <aside className={`glossary-panel ${open ? "show" : ""}`}>
        <h2>Prompt&nbsp;Glossary</h2>

        {/* scrollable body so long notes don't overflow */}
        <div className="glossary-body">
          <section>
            <h3>Naming conventions</h3>
            <p className="card">Business Units are called <strong>Segments</strong>. Example: <code>C&amp;I</code></p>
            <p className="card">Areas (<code>South</code>, <code>North</code>, <code>East</code>, <code>West</code>) are called <strong>Regions</strong>.</p>
            <p className="card">
              Area Manager codes follow: <br />
              <code>AM -&nbsp;YOUR-CODE</code><br />
              e.g.&nbsp;<code>AM - GOA</code>
            </p>
          </section>

          <section>
            <h3>Totals</h3>
            <p className="card">Use phrase <em>“total&nbsp;sales&nbsp;volume”</em> for aggregates.</p>
          </section>

          <section>
            <h3>Scope</h3>
            <p className="card">This agent is <strong>only</strong> for SQL queries; please avoid unrelated requests.</p>
          </section>

          <section>
            <h3>Example prompt</h3>
            <p className="card">
              What is the total sales volume for the <code>C&amp;I</code> segment by Region?
            </p>
          </section>

          <section>
            <h3>Example prompt 2</h3>
            <p className="card">
              What is the total sales volume for the <code> all segments</code> in the west region?
            </p>
            <p className="card">
              Please do not forget to mention <strong> region, segments</strong> when asking about total volume sales
            </p>
          </section>
        </div>
      </aside>
    </>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [glossaryOpen, setGlossaryOpen] = useState(true);

  const chatEndRef = useRef(null);
  const sid= getSessionId();

  /* ⬇ auto-scroll */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const { data } = await axios.post(
        `${import.meta.env.VITE_API_URL}/chat`,
        { question: input, session_id: sid }
      );
      const botMsg = { role: "assistant", content: data.answer };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg = {
        role: "assistant",
        content: `There was an error communicating with the server. Please Try Again later. ${
          err.response?.data?.detail ?? err.message
        }`,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };
  

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  useEffect(() => {
  const handleUnload = () => {
    /* fire-and-forget so it works during unload */
    console.log("Handling unload")
  };

  window.addEventListener("beforeunload", handleUnload);
  return () => window.removeEventListener("beforeunload", handleUnload);
}, [sid]);


  return (
    <div className="chat-wrapper">
      <h1>LangChain NL2SQL Chatbot</h1>

      <div className="chat-box">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {m.content}
            </ReactMarkdown>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="controls">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask me questions about sales!"
        />
        <button onClick={sendMessage} disabled={!input.trim() || loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
      {/* glossary */}
      <SideGlossary
        open={glossaryOpen}
        toggle={() => setGlossaryOpen((v) => !v)}
      />
    </div>
  );
}
