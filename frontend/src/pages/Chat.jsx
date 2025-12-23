import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const ask = async () => {
    if (!question.trim()) return;

    try {
      setLoading(true);

      const res = await axios.post(
        "http://localhost:8000/chat",
        null,
        { params: { question } }
      );

      setMessages([...messages, { q: question, a: res.data }]);
      setQuestion("");
    } catch (err) {
      setMessages([
        ...messages,
        {
          q: question,
          a: { summary: "Error processing your request." }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">

      {/* Header with Back Button */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3 className="mb-0">Ask Questions</h3>
        <button
          className="btn btn-outline-secondary"
          onClick={() => navigate("/")}
        >
          ← Back to Dashboard
        </button>
      </div>

      {/* Input */}
      <div className="input-group mb-3">
        <input
          className="form-control"
          placeholder="Ask a business question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button
          className="btn btn-primary"
          onClick={ask}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {/* Messages */}
      {messages.map((m, i) => (
        <div key={i} className="card mb-3 shadow-sm">
          <div className="card-body">
            <p><b>Asked Question:</b> {m.q}</p>

            {m.a.summary && (
              <p><b>System:</b> {m.a.summary}</p>
            )}

            {m.a.sql && (
              <>
                <p className="mb-1"><b>Generated SQL:</b></p>
                <pre className="bg-light p-2 rounded">
                  {m.a.sql}
                </pre>
              </>
            )}

            {m.a.data && m.a.data.length > 0 && (
              <div className="table-responsive mt-2">
                <table className="table table-bordered table-sm">
                  <thead className="table-light">
                    <tr>
                      {Object.keys(m.a.data[0]).map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {m.a.data.map((row, rIdx) => (
                      <tr key={rIdx}>
                        {Object.values(row).map((val, cIdx) => (
                          <td key={cIdx}>{val}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {m.a.data && m.a.data.length === 0 && (
              <p className="text-muted">No data returned.</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default Chat;
