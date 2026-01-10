import { useState, useCallback, useEffect } from "react";
import {
  Upload,
  FileSpreadsheet,
  X,
  Loader2,
  Database,
  TrendingUp,
  Brain,
  Sparkles,
} from "lucide-react";
import { Target, Info } from "lucide-react"; // Assuming Lucide is installed

//hiiii

export default function FileUpload({ onUpload, isUploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetColumn, setTargetColumn] = useState("");
  /* ================= SCROLL TO BOTTOM ================= */
  useEffect(() => {
    if (isUploading) {
      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: "smooth",
        });
      }, 100);
    }
  }, [isUploading]);

  /* ================= DRAG HANDLERS ================= */
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files?.[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "text/csv" || file.name.endsWith(".csv")) {
        setSelectedFile(file);
      }
    }
  }, []);
  const handleUploadClick = async () => {
  if (!selectedFile || isUploading) return;
  
  // 1. Send both file and target column
  const success = await onUpload(selectedFile, targetColumn.trim());
  
  // 2. Only reset the UI if the backend accepted the input
  if (success) {
    setSelectedFile(null);
    setTargetColumn("");
  }
};

  // const handleUpload = async () => {
  //   if (!selectedFile) return;
  //   await onUpload(selectedFile, targetColumn.trim());
  //   setSelectedFile(null);
  // };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <section className="pb-24">
      {/* ================= HERO ================= */}
      <div className="max-w-7xl mx-auto px-6 pt-5 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-600">
          <Sparkles className="h-4 w-4" />
          AI-Powered Dataset Analysis
        </div>

        <h1 className="mt-6 text-4xl md:text-5xl font-bold text-gray-900">
          Transform Data into{" "}
          <span className="text-indigo-600">Intelligent Insights</span>
        </h1>

        <p className="mt-5 max-w-3xl mx-auto text-lg text-gray-600">
          Upload your CSV dataset and let AI automatically detect problem types,
          recommend the best ML models, and answer your questions.
        </p>

        {/* ================= FEATURES ================= */}
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          <FeatureCard
            icon={<Database className="h-6 w-6 text-indigo-600" />}
            title="Smart Analysis"
            text="Automatic problem type detection, data quality checks, and feature importance analysis."
            bg="bg-indigo-50"
          />
          <FeatureCard
            icon={<TrendingUp className="h-6 w-6 text-emerald-600" />}
            title="Model Selection"
            text="Get recommendations for the best ML models with expected metrics and implementation tips."
            bg="bg-emerald-50"
          />
          <FeatureCard
            icon={<Brain className="h-6 w-6 text-green-600" />}
            title="AI Chat"
            text="Ask questions about your data and get intelligent, context-aware answers instantly."
            bg="bg-green-50"
          />
        </div>
      </div>

      {/* ================= UPLOAD BOX ================= */}
      <div className="max-w-5xl mx-auto px-6 mt-16">
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById("file-input")?.click()}
          className={`cursor-pointer rounded-2xl border-2 border-dashed p-14 text-center transition
            ${
              dragActive
                ? "border-indigo-500 bg-indigo-50"
                : "border-gray-300 bg-gray-50 hover:border-gray-400"
            }`}
        >
          <input
            id="file-input"
            type="file"
            accept=".csv"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="hidden"
          />
        
          {selectedFile ? (
            <div className="flex flex-col items-center gap-5">
              <div className="h-16 w-16 rounded-2xl bg-indigo-100 flex items-center justify-center">
                <FileSpreadsheet className="h-8 w-8 text-indigo-600" />
              </div>

              <div>
                <p className="font-medium">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                  className="rounded-md border px-4 py-2 text-sm hover:bg-gray-100"
                >
                  <X className="h-4 w-4 inline mr-1" />
                  Remove
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUploadClick();
                  }}
                  disabled={isUploading|| !selectedFile}
                  className="
                    rounded-md bg-black px-5 py-2 text-sm text-white
                    hover:bg-gray-800 transition
                    disabled:opacity-60 disabled:cursor-not-allowed
                  "
                >
                  {/* {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 inline mr-2 animate-spin" />
                      Uploading
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 inline mr-2" />
                      Analyze Dataset
                    </>
                  )} */}
                  {isUploading ? (
    <><Loader2 className="mr-2 animate-spin" /> Analyzing...</>
  ) : (
    <><Upload className="mr-2" /> Analyze Dataset</>
  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-6">
              <div className="h-20 w-20 rounded-full bg-indigo-100 flex items-center justify-center">
                <Upload className="h-10 w-10 text-indigo-600" />
              </div>

              <div>
                <p className="text-lg font-semibold">
                  Upload your CSV dataset
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  Drag & drop your file here, or click to browse
                </p>
              </div>

              <div className="inline-flex items-center gap-2 rounded-full border bg-white px-4 py-2 text-sm text-gray-600">
                <FileSpreadsheet className="h-4 w-4" />
                CSV files up to 20MB
              </div>
            </div>
          )}
        </div>
<div className="mt-6 max-w-md mx-auto space-y-2">
  <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
    <Target size={16} className="text-indigo-500" />
    Target Column Name
  </label>
  
  <div className="relative">
    <input
      type="text"
      placeholder="e.g. price, label, outcome"
      value={targetColumn}
      onChange={(e) => setTargetColumn(e.target.value)}
      className="w-full rounded-md border-gray-300 pl-4 pr-10 py-2.5 text-sm 
                 shadow-sm transition-shadow focus:ring-2 focus:ring-indigo-500 
                 focus:border-indigo-500 placeholder:text-gray-400"
    />
    <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
       <Info size={14} className="text-gray-300" />
    </div>
  </div>
  
  <p className="text-[11px] text-gray-400 flex items-center gap-1">
    <span className="font-medium text-indigo-600">Pro tip:</span> 
    Auto-detection works best with labeled datasets.
  </p>
</div>
      </div>
    </section>
  );
}

/* ================= FEATURE CARD ================= */
function FeatureCard({ icon, title, text, bg }) {
  return (
    <div className="rounded-2xl border bg-white p-8 text-center shadow-sm hover:shadow-md transition">
      <div
        className={`mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-xl ${bg}`}
      >
        {icon}
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-gray-600 leading-relaxed">{text}</p>
    </div>
  );
}