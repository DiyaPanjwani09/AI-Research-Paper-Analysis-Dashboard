import React from 'react';
import { FaExclamationTriangle, FaSyncAlt } from 'react-icons/fa';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-dark-950 p-8">
          <div className="glass-card p-8 max-w-md text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-red-500/10 border border-red-500/25 flex items-center justify-center">
              <FaExclamationTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="font-heading text-2xl font-bold text-white">Something went wrong</h2>
            <p className="text-dark-400 text-sm">
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              <FaSyncAlt className="w-4 h-4" /> Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
