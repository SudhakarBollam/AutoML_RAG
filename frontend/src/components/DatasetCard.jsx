import {
  FileSpreadsheet,
  Trash2,
  BarChart3,
  Loader2,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

export default function DatasetCard({ dataset, onDelete, onSelect }) {
  const formatFileSize = (bytes) => {
    if (!bytes && bytes !== 0) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusBadge = () => {
    const base =
      'inline-flex items-center px-2 py-1 text-xs rounded border';

    switch (dataset.analysis_status) {
      case 'completed':
        return (
          <span className={`${base} bg-green-100 text-green-700 border-green-300`}>
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Analyzed
          </span>
        );
      case 'analyzing':
        return (
          <span className={`${base} bg-blue-100 text-blue-700 border-blue-300`}>
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Analyzing
          </span>
        );
      case 'failed':
        return (
          <span className={`${base} bg-red-100 text-red-700 border-red-300`}>
            <AlertCircle className="w-3 h-3 mr-1" />
            Failed
          </span>
        );
      default:
        return (
          <span className={`${base} bg-gray-100 text-gray-600 border-gray-300`}>
            Pending
          </span>
        );
    }
  };

  const getProblemTypeBadge = () => {
    if (!dataset.problem_type) return null;

    const colors = {
      classification: 'bg-indigo-100 text-indigo-700 border-indigo-300',
      regression: 'bg-purple-100 text-purple-700 border-purple-300',
      clustering: 'bg-teal-100 text-teal-700 border-teal-300',
      semi_supervised: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    };

    return (
      <span
        className={`inline-flex items-center px-2 py-1 text-xs rounded border ${
          colors[dataset.problem_type] ||
          'bg-gray-100 text-gray-600 border-gray-300'
        }`}
      >
        {dataset.problem_type.replace('_', '-')}
      </span>
    );
  };

  return (
    <div
      className="group border rounded-xl p-4 bg-white hover:shadow-sm transition cursor-pointer"
      onClick={() => onSelect(dataset)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <FileSpreadsheet className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold line-clamp-1">
              {dataset.name}
            </h3>
            <p className="text-sm text-gray-500">
              {formatFileSize(dataset.file_size)}
            </p>
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(dataset.id);
          }}
          className="opacity-0 group-hover:opacity-100 p-2 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 transition"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-4">
        {getStatusBadge()}
        {getProblemTypeBadge()}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <p className="text-gray-500">Rows</p>
          <p className="font-semibold">
            {dataset.analysis_result?.statistical_summary?.total_rows?.toLocaleString() || '-'}
          </p>
        </div>
        <div>
          <p className="text-gray-500">Columns</p>
          <p className="font-semibold">
            {dataset.analysis_result?.statistical_summary?.total_columns || '-'}
          </p>
        </div>
      </div>

      {/* Best Model */}
      {dataset.analysis_result?.best_model && (
        <div className="mb-4 p-3 rounded-lg bg-indigo-50 border border-indigo-200">
          <p className="text-xs text-gray-500 mb-1">Best Model</p>
          <p className="font-medium text-indigo-700">
            {dataset.analysis_result.best_model.name}
          </p>
        </div>
      )}

      {/* Action */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onSelect(dataset);
        }}
        disabled={dataset.analysis_status !== 'completed'}
        className="w-full flex items-center justify-center px-3 py-2 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <BarChart3 className="w-4 h-4 mr-2" />
        View Analysis
      </button>
    </div>
  );
}