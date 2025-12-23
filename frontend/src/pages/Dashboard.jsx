import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Dashboard() {
  const [kpis, setKpis] = useState({});
  const [files, setFiles] = useState([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [preview, setPreview] = useState([]);

  const navigate = useNavigate();

  const loadDashboard = async () => {
    const res = await axios.get("http://localhost:8000/dashboard");
    setKpis(res.data.kpis || {});
    setFiles(res.data.files || []);
  };

  const loadPreview = async (table) => {
    setSelectedTable(table);

    if (!table) {
      setPreview([]);
      return;
    }

    const res = await axios.get(
      "http://localhost:8000/preview",
      { params: { table } }
    );

    setPreview(res.data.data || []);
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  return (
    <>
      {/* Navbar */}
      <nav className="navbar navbar-dark bg-dark">
        <div className="container">
          <span className="navbar-brand fw-bold">
            Text-to-SQL Analytics
          </span>

          <div>
            <button
              className="btn btn-outline-light me-2"
              onClick={() => navigate("/upload")}
            >
              Upload Excel
            </button>
            <button
              className="btn btn-success"
              onClick={() => navigate("/chat")}
              disabled={files.length === 0}
            >
              Ask Questions
            </button>
          </div>
        </div>
      </nav>

      <div className="container mt-4">

        {/* Uploaded Files List */}
        <h5 className="mb-3">Uploaded Files</h5>
        <table className="table table-bordered table-sm mb-4">
          <thead className="table-light">
            <tr>
              <th>File Name</th>
              <th>Sheets</th>
              <th>Uploaded At</th>
            </tr>
          </thead>
          <tbody>
            {files.map((f, i) => (
              <tr key={i}>
                <td>{f.filename}</td>
                <td>{f.tables.join(", ")}</td>
                <td>{f.uploaded_at}</td>
              </tr>
            ))}
            {files.length === 0 && (
              <tr>
                <td colSpan="3" className="text-muted text-center">
                  No files uploaded yet
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Sheet Selector */}
        <h5 className="mb-3">Select Sheet for Preview</h5>
        <select
          className="form-select mb-3"
          value={selectedTable}
          onChange={(e) => loadPreview(e.target.value)}
        >
          <option value="">-- Select a sheet --</option>

          {files.map((file, idx) => (
            <optgroup
              key={idx}
              label={`${file.filename} (${file.uploaded_at})`}
            >
              {file.tables.map((table) => (
                <option key={table} value={table}>
                  {table}
                </option>
              ))}
            </optgroup>
          ))}
        </select>

        {/* Data Preview */}
        <h5 className="mb-3">Data Preview</h5>
        {preview.length > 0 ? (
          <div className="table-responsive">
            <table className="table table-bordered table-sm">
              <thead className="table-light">
                <tr>
                  {Object.keys(preview[0]).map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-muted">
            Select a sheet to preview its data.
          </p>
        )}

      </div>
    </>
  );
}

export default Dashboard;
