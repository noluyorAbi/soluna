// app/loading.tsx

export default function Loading() {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 rounded-full bg-blue-600 animate-bounce"></div>
          <div className="w-4 h-4 rounded-full bg-blue-600 animate-bounce delay-75"></div>
          <div className="w-4 h-4 rounded-full bg-blue-600 animate-bounce delay-150"></div>
        </div>
        <p className="text-gray-700 text-lg mt-4">
          Lade Clan-Aktivitätsdaten...
        </p>
      </div>
    );
  }
  