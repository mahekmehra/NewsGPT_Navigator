import TopicInput from "../components/TopicInput";

export default function Dashboard({ onAnalyze, isLoading }) {
  return (
    <div>
      <TopicInput onAnalyze={onAnalyze} isLoading={isLoading} />
    </div>
  );
}
