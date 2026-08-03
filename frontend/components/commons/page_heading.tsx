// 목적: 각 화면 상단의 제목 영역을 공통 형태로 제공한다.
// 주요 역할: 화면 이름과 한 줄 설명을 같은 크기와 간격으로 표시한다.

interface PageHeadingProps {
  title: string;
  description: string;
}

export default function PageHeading({ title, description }: PageHeadingProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold text-ink">{title}</h1>
      <p className="mt-2 text-base text-ink-soft">{description}</p>
    </div>
  );
}
