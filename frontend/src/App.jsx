import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import NavLink from './components/NavLink';
import FileUpload from './components/FileUpload';
import DatasetCard from './components/DatasetCard';
import AnalysisView from './components/AnalysisView';
import ChatInterface from './components/ChatInterface';

export default function App() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [chatDataset, setChatDataset] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  /* ---------------- Upload Handler ---------------- */
  // App.jsx
// App.jsx
const handleUpload = async (file, targetCol) => { // 1. Accept targetCol
  setIsUploading(true);
  const formData = new FormData();
  formData.append('file', file);
  
  // 2. IMPORTANT: Send the target column to the backend
  if (targetCol) {
    formData.append('target_column', targetCol);
  }

  try {
    const response = await fetch('http://localhost:8000/api/v1/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error("Server error during upload");
    
    const initialData = await response.json();
    
    // 3. CHECK FOR TYPO BEFORE ADDING CARD
    // App.jsx inside handleUpload
if (initialData.analysis_status === 'needs_user_input') {
    const suggestions = initialData.suggested_targets;
    const suggestionText = suggestions && suggestions.length > 0 
        ? suggestions.join(', ') 
        : "no similar columns found. Please check your spelling.";

    alert(`Target column "${targetCol}" not found. Did you mean: ${suggestionText}`);
    
    setIsUploading(false);
    return false; // Prevents clearing FileUpload and adding the card
}

    // 4. SUCCESS: Add the card only if no typo was found
    setDatasets((prev) => [initialData, ...prev]);

    // Start Polling...
    const pollInterval = setInterval(async () => {
      try {
        const statusRes = await fetch(`http://localhost:8000/api/v1/dataset/${initialData.id}`);
        const updatedData = await statusRes.json();

        if (updatedData.analysis_status === 'completed') {
          setDatasets((prev) => prev.map(d => d.id === initialData.id ? updatedData : d));
          clearInterval(pollInterval);
        } else if (updatedData.analysis_status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (err) {
        clearInterval(pollInterval);
      }
    }, 3000);

    return true; // Tells FileUpload to clear the inputs

  } catch (error) {
    console.error("Upload failed", error);
    alert("Failed to connect to backend. Is the server running?");
    return false;
  } finally {
    setIsUploading(false);
  }
};

  /* ---------------- Delete Handler ---------------- */
  const handleDelete = (id) => {
    setDatasets((prev) => prev.filter((d) => d.id !== id));
    if (selectedDataset?.id === id) setSelectedDataset(null);
    if (chatDataset?.id === id) setChatDataset(null);
  };

  /* ---------------- Layout ---------------- */
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />

        <div className="flex flex-1">
          <NavLink />

          <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
            <Routes>
              <Route
                path="/"
                element={
                  <>
                    {/* HOME VIEW */}
                    {!selectedDataset && !chatDataset && (
                      <>
                        <FileUpload
                          onUpload={handleUpload}
                          isUploading={isUploading}
                        />

                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                          {datasets.map((dataset) => (
                            <DatasetCard
                              key={dataset.id}
                              dataset={dataset}
                              onDelete={handleDelete}
                              onSelect={setSelectedDataset}
                              onChat={setChatDataset}
                            />
                          ))}
                        </div>
                      </>
                    )}

                    {/* NEEDS USER INPUT VIEW */}
                    {selectedDataset?.analysis_status === 'needs_user_input' && (
                      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <h2 className="text-lg font-semibold text-yellow-800">
                          Action Required
                        </h2>
                        <p className="mt-2 text-sm text-yellow-700">
                          Please choose a valid target column to continue analysis.
                        </p>
                      </div>
                    )}

                    {/* ANALYSIS VIEW */}
                    {selectedDataset?.analysis_status === 'completed' && (
                      <AnalysisView
                        dataset={selectedDataset}
                        onBack={() => setSelectedDataset(null)}
                        onChat={() => {
                          setChatDataset(selectedDataset);
                          setSelectedDataset(null);
                        }}
                      />
                    )}

                    {/* CHAT VIEW */}
                    {chatDataset && (
                      <ChatInterface
                        dataset={chatDataset}
                        onBack={() => setChatDataset(null)}
                      />
                    )}
                  </>
                }
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}