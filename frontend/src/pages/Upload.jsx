import { useState } from "react";
import axios from "axios";

function Upload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select an Excel file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setStatus("");

      const res = await axios.post(
        "http://localhost:8000/upload",
        formData
      );

      setStatus("File Uploaded successfully");
      setTimeout(() => window.location.href = "/", 1500);

    } catch (err) {
      setStatus("❌ Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow border-0">
            <div className="card-body">
              <h4 className="card-title mb-3">
                Upload Excel File
              </h4>

              <p className="text-muted">
                Upload an Excel (.xlsx) file to automatically
                generate insights and enable chat queries.
              </p>

              <input
                type="file"
                className="form-control mb-3"
                accept=".xlsx"
                onChange={(e) => setFile(e.target.files[0])}
              />

              <button
                className="btn btn-primary w-100"
                onClick={handleUpload}
                disabled={loading}
              >
                {loading ? "Uploading..." : "Upload"}
              </button>

              {status && (
                <div className="alert alert-info mt-3">
                  {status}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Upload;
