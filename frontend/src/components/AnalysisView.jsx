import { useState ,useEffect} from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  ArrowLeft,
  Download,
  Brain,
  Lightbulb,
  Wrench,
  BarChart2,
  TrendingUp,
  AlertTriangle,
  Target,
  CheckCircle,
  Loader2, 
} from 'lucide-react';

export default function AnalysisView({ dataset, onBack, onChat }) {
  
  const analysis = dataset?.analysis_result;
  const [activeTab, setActiveTab] = useState('models');
  const [ragStatus, setRagStatus] = useState(dataset?.rag_status ?? 'pending');
  console.log(dataset.analysis_status, dataset.analysis_result);
  if (
    !dataset ||
    dataset.analysis_status !== "completed" ||
    !analysis ||
    !analysis.statistical_summary
  ) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
        <h3 className="text-lg font-semibold mb-2">Analysis Not Ready</h3>
        <p className="text-gray-500 mb-4">
          Waiting for valid analysis results.
        </p>
        <button
          onClick={onBack}
          className="px-4 py-2 border rounded-md hover:bg-gray-50"
        >
          Go Back
        </button>
      </div>
    );
  }

useEffect(() => {
  if (ragStatus === 'ready') return;

  const interval = setInterval(async () => {
  const res = await fetch(`http://localhost:8000/api/v1/dataset/${dataset.id}`);
    const data = await res.json();
    setRagStatus(data.rag_status);
  }, 3000);

  return () => clearInterval(interval);
}, [ragStatus, dataset.id]);


  if (!analysis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
        <h3 className="text-lg font-semibold mb-2">Analysis Not Available</h3>
        <p className="text-gray-500 mb-4">
          The analysis results are not available for this dataset.
        </p>
        <button
          onClick={onBack}
          className="px-4 py-2 border rounded-md hover:bg-gray-50"
        >
          Go Back
        </button>
      </div>
    );
  }

  const importanceColor = (level) => {
    switch (level) {
      case 'high':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'low':
        return 'bg-gray-100 text-gray-600 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 rounded-md hover:bg-gray-100"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div>
            <h1 className="text-2xl font-bold">{dataset.name}</h1>
            <p className="text-gray-500">{dataset.original_filename}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <button className="flex items-center px-3 py-2 border rounded-md text-sm hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>

          {ragStatus === 'ready' ? (
  <button
    onClick={onChat}
    className="flex items-center px-3 py-2 bg-black text-white rounded-md"
  >
    <Brain className="w-4 h-4 mr-2" />
    Ask Questions
  </button>
) : (
  <div className="text-sm text-gray-500 flex items-center gap-2">
    <Loader2 className="w-4 h-4 animate-spin" />
    Preparing chat (indexing embeddings)...
  </div>
)}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<BarChart2 className="w-4 h-4 text-blue-500" />}
          label="Rows"
          value={analysis.statistical_summary.total_rows.toLocaleString()}
        />
        <StatCard
          icon={<Target className="w-4 h-4 text-red-500" />}
          label="Target Column"
          value={analysis.target_column}
        />
        <StatCard
          icon={<Target className="w-4 h-4 text-purple-500" />}
          label="Columns"
          value={analysis.statistical_summary.total_columns}
        />
        <StatCard
          icon={<TrendingUp className="w-4 h-4 text-green-500" />}
          label="Problem Type"
          value={analysis.problem_type.replace('_', ' ')}
        />
        <StatCard
          icon={<CheckCircle className="w-4 h-4 text-emerald-500" />}
          label="Best Model"
          value={analysis.best_model.name}
        />
      </div>

      {/* Tabs */}
      <div>
        <div className="flex border-b">
          {['models', 'metrics', 'features','distributions','insights', 'preprocessing'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-sm font-medium border-b-2 ${
                activeTab === tab
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-black'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* MODELS */}
        {activeTab === 'models' && (
          <div className="mt-6 space-y-6">
            <div className="border rounded-xl p-6 bg-gray-50">
              <div className="flex justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold">
                    {analysis.best_model.name}
                  </h3>
                  <p className="text-gray-500">
                    {analysis.best_model.algorithm}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">Confidence</p>
                  <p className="text-2xl font-bold">
                    {analysis.best_model.confidence}%
                  </p>
                </div>
              </div>
              <p className="mb-4">{analysis.best_model.reasoning}</p>
              <div className="bg-white p-4 rounded-md border">
                <p className="text-sm font-semibold mb-1">
                  Why this model?
                </p>
                <p className="text-sm text-gray-600">
                  {analysis.best_model.reasoning}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* FEATURES */}
        {activeTab === 'features' && (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full border text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {[
                    'Feature',
                    'Type',
                    'Unique',
                    'Missing %',
                    'Importance',
                    'Description',
                  ].map((h) => (
                    <th key={h} className="p-3 text-left border">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {analysis.feature_analysis.map((f, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-3 font-mono">{f.name}</td>
                    <td className="p-3">{f.type}</td>
                    <td className="p-3">{f.unique_values}</td>
                    <td className="p-3">{f.missing_percentage}%</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-1 text-xs border rounded ${importanceColor(
                          f.importance
                        )}`}
                      >
                        {f.importance}
                      </span>
                    </td>
                    <td className="p-3 text-gray-600">{f.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {/* METRICS */}
        {activeTab === 'metrics' && (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full border text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score'].map(h => (
                    <th key={h} className="p-3 border text-left">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {analysis.model_metrics.map((m, i) => (
                  <tr key={i} className="border-t">
                    <td className="p-3 font-semibold">{m.model}</td>
                    <td className="p-3">{(m.accuracy * 100).toFixed(2)}%</td>
                    <td className="p-3">{(m.precision * 100).toFixed(2)}%</td>
                    <td className="p-3">{(m.recall * 100).toFixed(2)}%</td>
                    <td className="p-3">{(m.f1_score * 100).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {/* DISTRIBUTIONS */}
        {activeTab === 'distributions' && (
          <div className="mt-6 overflow-x-auto">
            {analysis.numeric_distributions &&
            Object.keys(analysis.numeric_distributions).length > 0 ? (
              <table className="w-full border text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {[
                      'Feature',
                      'Mean',
                      'Median',
                      'Std',
                      'Min',
                      'Max',
                      'Skewness',
                    ].map((h) => (
                      <th key={h} className="p-3 text-left border">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analysis.numeric_distributions).map(
                    ([feature, stats], i) => (
                      <tr key={i} className="border-t">
                        <td className="p-3 font-mono">{feature}</td>
                        <td className="p-3">{stats.mean}</td>
                        <td className="p-3">{stats.median}</td>
                        <td className="p-3">{stats.std}</td>
                        <td className="p-3">{stats.min}</td>
                        <td className="p-3">{stats.max}</td>
                        <td className="p-3">{stats.skewness}</td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-500">
                No numeric distributions available for this dataset.
              </p>
            )}
          </div>
        )}


        {/* INSIGHTS */}
        {activeTab === 'insights' && (
          <div className="mt-6 grid md:grid-cols-2 gap-4">
            {analysis.insights.map((insight, i) => (
              <div
                key={i}
                className="border rounded-lg p-4 bg-white space-y-2"
              >
                <div className="flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-yellow-500" />
                  <span
                    className={`px-2 py-1 text-xs border rounded ${importanceColor(
                      insight.importance
                    )}`}
                  >
                    {insight.importance}
                  </span>
                </div>
                <h4 className="font-semibold">{insight.title}</h4>
                <p className="text-sm text-gray-600">
                  {insight.description}
                </p>
              </div>
            ))}
          </div>
        )}
        {activeTab === "preprocessing" && (
        <div className="mt-6 space-y-8">

          {/* FLOWCHART */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Preprocessing Flow</h3>
            <div className="flex flex-wrap items-center gap-3 text-sm">
              {analysis?.preprocessing_report?.flow?.map((step, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="px-3 py-2 border rounded bg-gray-50 font-medium">
                    {step}
                  </div>
                  {i < analysis.preprocessing_report.flow.length - 1 && (
                    <span className="text-gray-400">→</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* STRATEGY SUMMARY */}
          <div className="border rounded-lg p-4 bg-white">
            <h4 className="font-semibold mb-2">Preprocessing Summary</h4>
            <p className="text-sm text-gray-700">
              Numeric features were processed using <b>{analysis.preprocessing_report.numeric_strategy}</b>.
              Categorical features were processed using <b>{analysis.preprocessing_report.categorical_strategy}</b>.
              Feature space expanded from{" "}
              <b>{analysis.preprocessing_report.total_features_before}</b> to{" "}
              <b>{analysis.preprocessing_report.total_features_after}</b> features.
            </p>
          </div>

          {/* MISSING VALUES BAR CHART */}
          <div>
            <h4 className="font-semibold mb-3">Missing Values (Before Preprocessing)</h4>

            {Object.keys(analysis.missing_summary).length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={Object.entries(analysis.missing_summary).map(
                    ([feature, missing]) => ({ feature, missing })
                  )}
                >
                  <XAxis dataKey="feature" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="missing" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-500">No missing values detected.</p>
            )}
          </div>

          {/* NUMERIC DISTRIBUTIONS TABLE */}
          <div>
            <h4 className="font-semibold mb-3">Numeric Feature Distributions (Raw Data)</h4>

            <div className="overflow-x-auto">
              <table className="w-full border text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    {["Feature", "Mean", "Median", "Std", "Min", "Max", "Skewness"].map(h => (
                      <th key={h} className="p-3 border text-left">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analysis.numeric_distributions).map(
                    ([feature, stats], i) => (
                      <tr key={i} className="border-t">
                        <td className="p-3 font-mono">{feature}</td>
                        <td className="p-3">{stats.mean}</td>
                        <td className="p-3">{stats.median}</td>
                        <td className="p-3">{stats.std}</td>
                        <td className="p-3">{stats.min}</td>
                        <td className="p-3">{stats.max}</td>
                        <td className="p-3">{stats.skewness}</td>
                      </tr>
                    )
                  )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  )}

        
      </div>
    </div>
  );
}

/* ---------- Helper ---------- */

function StatCard({ icon, label, value }) {
  return (
    <div className="border rounded-lg p-4 bg-white">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <p className="text-xl font-bold">{value}</p>
    </div>
  );
}