"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type DataRow = Record<string, unknown>;

type Analysis = {
  summary: string;
  insights: string[];
};

type ChartPlan = {
  chart_type: string;
  x_axis?: string | null;
  y_axis?: string | null;
  title?: string | null;
  reason?: string | null;
};

type Visualization = {
  plan: ChartPlan;
  chart?: Record<string, unknown>;
};

type AnalyticsResult = {
  question: string;
  sql: string;

  data: {
    columns: string[];
    rows: DataRow[];
    row_count: number;
  };

  analysis: Analysis;

  visualization?: Visualization | null;

  metadata: {
    attempts: number;
    corrections: number;
    execution_time_ms: number;
  };

  attempts: number;
  corrections: number;

  columns?: string[];
  rows?: DataRow[];
  row_count?: number;
};

type HistoryItem = {
  id: string;
  question: string;
  timestamp: string;
  result: AnalyticsResult;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://sql-coder-api.onrender.com";

const SUGGESTIONS = [
  "Quais foram os 3 produtos mais vendidos?",
  "Qual produto vendeu mais?",
  "Qual produto teve maior faturamento?",
  "Mostre os produtos e suas vendas",
];

function formatNumber(value: unknown): string {
  if (typeof value === "number") {
    return new Intl.NumberFormat("pt-BR").format(value);
  }

  if (typeof value === "string") {
    const numeric = Number(value);

    if (!Number.isNaN(numeric)) {
      return new Intl.NumberFormat("pt-BR").format(numeric);
    }
  }

  return String(value ?? "-");
}

function formatCurrency(value: unknown): string {
  const numeric = Number(value);

  if (Number.isNaN(numeric)) {
    return String(value ?? "-");
  }

  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(numeric);
}

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "-";
  }

  if (typeof value === "number") {
    return new Intl.NumberFormat("pt-BR").format(value);
  }

  if (typeof value === "boolean") {
    return value ? "Sim" : "Não";
  }

  return String(value);
}

function formatDate(value: string): string {
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function isNumeric(value: unknown): boolean {
  if (typeof value === "number") {
    return Number.isFinite(value);
  }

  if (typeof value === "string" && value.trim() !== "") {
    return Number.isFinite(Number(value));
  }

  return false;
}

function getNumericColumns(
  columns: string[],
  rows: DataRow[],
): string[] {
  return columns.filter((column) =>
    rows.some((row) => isNumeric(row[column])),
  );
}

function getChartData(
  result: AnalyticsResult,
): Array<{
  label: string;
  value: number;
}> {
  const columns = result.data.columns;
  const rows = result.data.rows;

  if (!columns.length || !rows.length) {
    return [];
  }

  const plan = result.visualization?.plan;

  let xAxis = plan?.x_axis ?? columns[0];

  let yAxis = plan?.y_axis ?? null;

  if (!yAxis) {
    const numericColumns = getNumericColumns(columns, rows);
    yAxis = numericColumns[0] ?? null;
  }

  if (!yAxis) {
    return [];
  }

  if (!columns.includes(xAxis)) {
    xAxis = columns[0];
  }

  return rows
    .map((row) => ({
      label: String(row[xAxis] ?? "-"),
      value: Number(row[yAxis] ?? 0),
    }))
    .filter((item) => Number.isFinite(item.value))
    .slice(0, 12);
}

function calculateKpis(result: AnalyticsResult) {
  const columns = result.data.columns;
  const rows = result.data.rows;

  const numericColumns = getNumericColumns(columns, rows);

  const primaryNumericColumn = numericColumns[0];

  if (!primaryNumericColumn) {
    return {
      total: rows.length,
      sum: null,
      average: null,
      maximum: null,
    };
  }

  const values = rows
    .map((row) => Number(row[primaryNumericColumn]))
    .filter((value) => Number.isFinite(value));

  if (!values.length) {
    return {
      total: rows.length,
      sum: null,
      average: null,
      maximum: null,
    };
  }

  const sum = values.reduce((acc, value) => acc + value, 0);

  return {
    total: rows.length,
    sum,
    average: sum / values.length,
    maximum: Math.max(...values),
  };
}

function getResultData(result: AnalyticsResult) {
  return {
    columns: result.data?.columns ?? result.columns ?? [],
    rows: result.data?.rows ?? result.rows ?? [],
    rowCount:
      result.data?.row_count ??
      result.row_count ??
      result.data?.rows?.length ??
      result.rows?.length ??
      0,
  };
}

function getFriendlyChartType(chartType?: string): string {
  if (!chartType) {
    return "Visualização";
  }

  const types: Record<string, string> = {
    bar: "Gráfico de barras",
    line: "Gráfico de linha",
    pie: "Gráfico de pizza",
    doughnut: "Gráfico de rosca",
    area: "Gráfico de área",
    table: "Tabela",
  };

  return types[chartType.toLowerCase()] ?? chartType;
}

function ChartSection({
  result,
}: {
  result: AnalyticsResult;
}) {
  const chartData = getChartData(result);
  const plan = result.visualization?.plan;

  if (!plan || !chartData.length) {
    return null;
  }

  const maxValue = Math.max(...chartData.map((item) => item.value), 1);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-6">
      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Visualização
          </p>

          <h2 className="mt-1 text-lg font-semibold text-white">
            {plan.title || "Visualização dos dados"}
          </h2>
        </div>

        <span className="w-fit rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-500">
          {getFriendlyChartType(plan.chart_type)}
        </span>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 sm:p-6">
        <div className="flex h-72 items-end gap-2 overflow-x-auto pb-8 sm:gap-4">
          {chartData.map((item, index) => {
            const height = Math.max(
              (item.value / maxValue) * 100,
              4,
            );

            return (
              <div
                key={`${item.label}-${index}`}
                className="group flex h-full min-w-16 flex-1 flex-col justify-end"
              >
                <div className="relative flex h-full items-end">
                  <div
                    className="w-full rounded-t-lg bg-slate-300 transition-all duration-500 group-hover:bg-white"
                    style={{
                      height: `${height}%`,
                    }}
                    title={`${item.label}: ${formatNumber(item.value)}`}
                  />
                </div>

                <div className="mt-3 truncate text-center text-[11px] text-slate-500">
                  {item.label}
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-2 flex items-center justify-between border-t border-slate-800 pt-3 text-xs text-slate-600">
          <span>{plan.x_axis || "Categoria"}</span>
          <span>{plan.y_axis || "Valor"}</span>
        </div>
      </div>

      {plan.reason && (
        <p className="mt-4 text-xs leading-5 text-slate-600">
          {plan.reason}
        </p>
      )}
    </section>
  );
}

function DataExplorer({
  result,
}: {
  result: AnalyticsResult;
}) {
  const { columns, rows, rowCount } = getResultData(result);

  if (!columns.length) {
    return null;
  }

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-xl">
      <div className="flex flex-col gap-2 border-b border-slate-800 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Data Explorer
          </p>

          <h2 className="mt-1 text-lg font-semibold text-white">
            Dados retornados
          </h2>
        </div>

        <span className="w-fit rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-500">
          {rowCount} {rowCount === 1 ? "registro" : "registros"}
        </span>
      </div>

      <div className="max-h-[520px] max-w-full overflow-auto">
        <table className="min-w-full border-collapse">
          <thead className="sticky top-0 z-10 bg-slate-950">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={column}
                  className="whitespace-nowrap border-b border-slate-800 px-4 py-3 text-left text-xs font-semibold text-slate-400 sm:px-5 sm:py-4"
                >
                  <span className="mr-2 text-slate-700">
                    #
                  </span>
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-b border-slate-800/80 transition hover:bg-slate-800/40"
              >
                {columns.map((column) => (
                  <td
                    key={`${rowIndex}-${column}`}
                    className="whitespace-nowrap px-4 py-3 text-sm text-slate-300 sm:px-5 sm:py-3.5"
                  >
                    {formatCellValue(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SqlSection({
  sql,
}: {
  sql: string;
}) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl sm:p-6">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            SQL Gerado
          </p>

          <h2 className="mt-1 text-lg font-semibold text-white">
            Consulta executada
          </h2>
        </div>

        <span className="text-xs text-slate-600">
          Gerado automaticamente pelo agente
        </span>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
        <pre className="overflow-x-auto whitespace-pre-wrap break-words p-4 text-xs leading-6 text-slate-300 sm:p-5 sm:text-sm sm:leading-7">
          <code>{sql}</code>
        </pre>
      </div>
    </section>
  );
}

function AnalysisSection({
  result,
}: {
  result: AnalyticsResult;
}) {
  const analysis = result.analysis;

  if (!analysis) {
    return null;
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-6">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
        Análise
      </p>

      <p className="mt-2 text-base font-semibold leading-7 text-white sm:text-lg">
        {analysis.summary}
      </p>

      {analysis.insights?.length > 0 && (
        <div className="mt-6 space-y-3">
          {analysis.insights.map((insight, index) => (
            <div
              key={index}
              className="rounded-xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm leading-6 text-slate-300"
            >
              {insight}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function KpiCard({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl transition hover:border-slate-700 sm:p-6">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-3 break-words text-2xl font-bold tracking-tight text-white sm:text-3xl">
        {value}
      </p>

      {description && (
        <p className="mt-2 text-xs text-slate-600">
          {description}
        </p>
      )}
    </div>
  );
}

function KpiSection({
  result,
}: {
  result: AnalyticsResult;
}) {
  const kpis = calculateKpis(result);

  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        label="Registros"
        value={formatNumber(kpis.total)}
        description="Linhas retornadas"
      />

      <KpiCard
        label="Total"
        value={
          kpis.sum !== null
            ? formatCurrency(kpis.sum)
            : "—"
        }
        description="Soma do principal indicador"
      />

      <KpiCard
        label="Média"
        value={
          kpis.average !== null
            ? formatCurrency(kpis.average)
            : "—"
        }
        description="Média do indicador"
      />

      <KpiCard
        label="Maior valor"
        value={
          kpis.maximum !== null
            ? formatCurrency(kpis.maximum)
            : "—"
        }
        description="Maior valor encontrado"
      />
    </section>
  );
}

function MetadataSection({
  result,
}: {
  result: AnalyticsResult;
}) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-xs text-slate-600">Tentativas</p>
        <p className="mt-1 text-lg font-semibold text-white">
          {result.attempts}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-xs text-slate-600">Correções</p>
        <p className="mt-1 text-lg font-semibold text-white">
          {result.corrections}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-xs text-slate-600">Tempo</p>
        <p className="mt-1 text-lg font-semibold text-white">
          {result.metadata.execution_time_ms.toFixed(0)} ms
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
        <p className="text-xs text-slate-600">Status</p>
        <p className="mt-1 text-lg font-semibold text-white">
          Concluído
        </p>
      </div>
    </div>
  );
}

function HistorySection({
  history,
  onSelect,
  onClear,
}: {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onClear: () => void;
}) {
  if (!history.length) {
    return null;
  }

  return (
    <section className="mb-8">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-600">
            Histórico
          </p>

          <h2 className="mt-1 text-base font-semibold text-white">
            Consultas recentes
          </h2>
        </div>

        <button
          type="button"
          onClick={onClear}
          className="rounded-lg px-2 py-1 text-xs text-slate-600 transition hover:bg-slate-900 hover:text-slate-400"
        >
          Limpar histórico
        </button>
      </div>

      <div className="space-y-2">
        {history.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelect(item)}
            className="group flex w-full items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-left transition hover:border-slate-700 hover:bg-slate-950 sm:gap-4 sm:p-4"
          >
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-500 transition group-hover:text-white">
              ↗
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-300 group-hover:text-white">
                {item.question}
              </p>

              <p className="mt-1 text-xs text-slate-600">
                {formatDate(item.timestamp)}
              </p>
            </div>

            <div className="hidden shrink-0 items-center gap-2 text-xs text-slate-600 sm:flex">
              <span>Ver análise</span>
              <span className="text-slate-700">→</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

export default function Home() {
  const [question, setQuestion] = useState(
    "Quais foram os 3 produtos mais vendidos?",
  );

  const [result, setResult] =
    useState<AnalyticsResult | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem(
        "sql-coder-history",
      );

      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch {
      localStorage.removeItem("sql-coder-history");
    }
  }, []);

  const saveHistory = (newHistory: HistoryItem[]) => {
    setHistory(newHistory);

    try {
      localStorage.setItem(
        "sql-coder-history",
        JSON.stringify(newHistory),
      );
    } catch {
      // Ignora erros de armazenamento local.
    }
  };

  const analyzeQuestion = async (submittedQuestion?: string) => {
    const currentQuestion = (
      submittedQuestion ?? question
    ).trim();

    if (!currentQuestion) {
      setError("Digite uma pergunta antes de analisar.");
      return;
    }

    if (currentQuestion.length < 3) {
      setError(
        "A pergunta precisa ter pelo menos 3 caracteres.",
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/analytics/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: currentQuestion,
          }),
        },
      );

      let payload: unknown;

      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        if (
          typeof payload === "object" &&
          payload !== null &&
          "detail" in payload
        ) {
          throw new Error(
            String(
              (payload as { detail: unknown }).detail,
            ),
          );
        }

        throw new Error(
          `Erro HTTP ${response.status}.`,
        );
      }

      const analyticsResult =
        payload as AnalyticsResult;

      setResult(analyticsResult);
      setQuestion(currentQuestion);

      const historyItem: HistoryItem = {
        id: `${Date.now()}`,
        question: currentQuestion,
        timestamp: new Date().toISOString(),
        result: analyticsResult,
      };

      const updatedHistory = [
        historyItem,
        ...history.filter(
          (item) => item.question !== currentQuestion,
        ),
      ].slice(0, 10);

      saveHistory(updatedHistory);

      setTimeout(() => {
        document
          .getElementById("results")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 50);
    } catch (requestError) {
      if (requestError instanceof TypeError) {
        setError(
          "Não foi possível conectar ao servidor. Verifique se o FastAPI está rodando em http://127.0.0.1:8000.",
        );
      } else {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Não foi possível concluir a análise.",
        );
      }

      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    await analyzeQuestion();
  };

  const handleHistorySelect = (item: HistoryItem) => {
    setQuestion(item.question);
    setResult(item.result);
    setError("");

    setTimeout(() => {
      document
        .getElementById("results")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  };

  const clearHistory = () => {
    saveHistory([]);
  };

  const resultCount = useMemo(() => {
    if (!result) {
      return 0;
    }

    return getResultData(result).rowCount;
  }, [result]);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10">
        <header className="mb-8 sm:mb-10">
          <div className="flex items-start gap-3 sm:gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-xs font-bold text-slate-950 shadow-lg sm:h-11 sm:w-11">
              SQL
            </div>

            <div className="min-w-0">
              <p className="mb-1 text-xs font-medium tracking-wide text-slate-500 sm:text-sm">
                SQL-Coder & Analytics Agent
              </p>

              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl lg:text-4xl">
                Analytics Dashboard
              </h1>
            </div>
          </div>

          <div className="mt-4 flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-500" />

            <p className="max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
              Faça perguntas sobre seus dados em linguagem
              natural e deixe o agente gerar, executar e
              analisar o SQL automaticamente.
            </p>
          </div>
        </header>

        <section className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-6 lg:p-7">
          <form onSubmit={handleSubmit}>
            <label
              htmlFor="question"
              className="mb-3 block text-sm font-medium text-slate-300"
            >
              Faça uma pergunta sobre seus dados
            </label>

            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="relative flex-1">
                <input
                  id="question"
                  type="text"
                  value={question}
                  onChange={(event) =>
                    setQuestion(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Escape") {
                      setQuestion("");
                    }
                  }}
                  placeholder="Ex.: Quais foram os produtos mais vendidos?"
                  disabled={loading}
                  aria-label="Pergunta sobre os dados"
                  className="min-h-12 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 pr-12 text-white outline-none transition placeholder:text-slate-600 focus:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
                />

                {question.length > 0 && !loading && (
                  <button
                    type="button"
                    onClick={() => setQuestion("")}
                    aria-label="Limpar pergunta"
                    className="absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-800 hover:text-slate-300"
                  >
                    ×
                  </button>
                )}
              </div>

              <button
                type="submit"
                disabled={
                  loading || !question.trim()
                }
                className="min-h-12 rounded-xl bg-white px-7 font-semibold text-slate-950 shadow-lg transition hover:bg-slate-200 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-slate-950" />
                    Analisando...
                  </span>
                ) : (
                  "Analisar"
                )}
              </button>
            </div>
          </form>

          {!result && !loading && (
            <div className="mt-5">
              <p className="mb-3 text-xs font-medium uppercase tracking-wider text-slate-600">
                Experimente uma pergunta
              </p>

              <div className="flex flex-wrap gap-2">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() =>
                      setQuestion(suggestion)
                    }
                    className="rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-left text-xs text-slate-500 transition hover:border-slate-700 hover:bg-slate-800 hover:text-slate-300"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="mt-4 flex items-start gap-3 rounded-xl border border-red-900/60 bg-red-950/30 px-4 py-3"
            >
              <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-red-900/40 text-xs text-red-300">
                !
              </div>

              <div className="min-w-0">
                <p className="text-sm font-medium text-red-300">
                  Não foi possível concluir a análise
                </p>

                <p className="mt-1 break-words text-xs leading-5 text-red-400/80">
                  {error}
                </p>
              </div>
            </div>
          )}
        </section>

        {!result && !loading && (
          <HistorySection
            history={history}
            onSelect={handleHistorySelect}
            onClear={clearHistory}
          />
        )}

        {loading && (
          <section
            className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center shadow-xl sm:p-12"
            aria-live="polite"
            aria-busy="true"
          >
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-800 bg-slate-950">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-700 border-t-white" />
            </div>

            <h2 className="text-lg font-semibold">
              Analisando seus dados...
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              O agente está gerando o SQL, executando a
              consulta e preparando os resultados.
            </p>

            <div className="mx-auto mt-6 max-w-sm overflow-hidden rounded-full bg-slate-800">
              <div className="h-1 w-1/2 animate-pulse rounded-full bg-slate-400" />
            </div>
          </section>
        )}

        {result && !loading && (
          <div
            id="results"
            className="space-y-6"
          >
            <div className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:flex-row sm:items-center sm:justify-between sm:p-6">
              <div className="min-w-0">
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Resultado da consulta
                </p>

                <h2 className="mt-1 break-words text-lg font-semibold text-white">
                  {result.question}
                </h2>
              </div>

              <button
                type="button"
                onClick={() =>
                  analyzeQuestion(result.question)
                }
                disabled={loading}
                className="w-full shrink-0 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:border-slate-600 hover:text-white disabled:opacity-50 sm:w-auto"
              >
                ↻ Executar novamente
              </button>
            </div>

            <KpiSection result={result} />

            <AnalysisSection result={result} />

            <ChartSection result={result} />

            <DataExplorer result={result} />

            <SqlSection sql={result.sql} />

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl sm:p-6">
              <div className="mb-5">
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Execução
                </p>

                <h2 className="mt-1 text-lg font-semibold text-white">
                  Detalhes da análise
                </h2>
              </div>

              <MetadataSection result={result} />
            </section>

            <div className="flex flex-col gap-3 border-t border-slate-900 pt-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs text-slate-600">
                {resultCount}{" "}
                {resultCount === 1
                  ? "registro encontrado"
                  : "registros encontrados"}
              </p>

              <button
                type="button"
                onClick={() => {
                  setResult(null);
                  setError("");

                  setTimeout(() => {
                    document
                      .getElementById("question")
                      ?.focus();
                  }, 50);
                }}
                className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-400 transition hover:border-slate-700 hover:text-white sm:w-auto"
              >
                Nova análise
              </button>
            </div>

            <HistorySection
              history={history}
              onSelect={handleHistorySelect}
              onClear={clearHistory}
            />
          </div>
        )}

        <footer className="mt-12 border-t border-slate-900 pt-6 text-center text-xs text-slate-700">
          SQL-Coder & Analytics Agent · Natural Language →
          SQL → Analytics
        </footer>
      </div>
    </main>
  );
}