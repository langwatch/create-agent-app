import {
  CopilotKit,
  useCopilotAction,
  type CatchAllActionRenderProps,
} from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import ReactMarkdown from "react-markdown";
import { useState } from "react";
import type {
  DocumentResponse,
  OrderSummaryResponse,
} from "@langwatch/create-agent-app";

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:4111/copilotkit"
      agent="customerSupportAgent"
    >
      <CustomerSupportChat />
    </CopilotKit>
  );
}

function CustomerSupportChat() {
  useCopilotAction({
    name: "*",
    render: (({ name, status, result }: CatchAllActionRenderProps) => {
      if (status === "executing") {
        return (
          <div className="flex items-center justify-center p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-blue-700 font-medium">
                Calling tool: {name}
              </span>
            </div>
          </div>
        );
      }

      if (status === "complete") {
        if (name === "getCustomerOrderHistoryTool") {
          return <OrderHistoryTable orders={result} />;
        }

        if (
          name === "getCompanyPolicyTool" ||
          name === "getTroubleshootingGuideTool"
        ) {
          return <DocumentViewer document={result} />;
        }

        if (name === "escalateToHumanTool") {
          return <EscalationModal />;
        }
      }

      return null;
    }) as (props: CatchAllActionRenderProps) => React.ReactElement,
  });

  return (
    <div className="max-w-2xl mx-auto">
      <CopilotChat
        labels={{
          title: "Your Assistant",
          initial: "Hi! 👋 How can I assist you today?",
        }}
      />
    </div>
  );
}

const EscalationModal = () => {
  const [isModalOpen, setIsModalOpen] = useState(true);

  const handleConfirmEscalation = () => {
    // Here you would typically call an API to escalate to human support
    alert(
      "Your request has been escalated to human support. A representative will be with you shortly."
    );
    setIsModalOpen(false);
  };

  const handleCancel = () => {
    setIsModalOpen(false);
  };

  if (!isModalOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#00000060] flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
        <div className="bg-gradient-to-r from-orange-500 to-red-500 px-6 py-4">
          <div className="flex items-center space-x-3">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a2 2 0 01-2-2v-6a2 2 0 012-2h8z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-white">
              Connect with Human Support
            </h3>
          </div>
          <p className="text-orange-100 text-sm mt-1">
            Get help from our support team
          </p>
        </div>

        <div className="px-6 py-6">
          <div className="mb-6">
            <p className="text-gray-700 mb-4">
              Our AI assistant has determined that your request would be best
              handled by a human representative. Our support team is standing by
              to provide personalized assistance.
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-center space-x-2">
                <svg
                  className="w-5 h-5 text-blue-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="text-blue-800 text-sm font-medium">
                  A support representative will be with you shortly
                </p>
              </div>
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleConfirmEscalation}
              className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white font-medium py-3 px-4 rounded-lg hover:from-orange-600 hover:to-red-600 transition-all duration-200 flex items-center justify-center space-x-2"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a2 2 0 01-2-2v-6a2 2 0 012-2h8z"
                />
              </svg>
              <span>Connect Now</span>
            </button>

            <button
              onClick={handleCancel}
              className="flex-1 bg-gray-100 text-gray-700 font-medium py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors duration-200"
            >
              Continue Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const OrderHistoryTable = ({ orders }: { orders: OrderSummaryResponse[] }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">Order History</h3>
        <p className="text-blue-100 text-sm mt-1">Customer's recent orders</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {orders.map((order: OrderSummaryResponse, index: number) => (
              <tr
                key={order.orderId}
                className={`hover:bg-gray-50 transition-colors duration-150 ${
                  index % 2 === 0 ? "bg-white" : "bg-gray-25"
                }`}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {order.orderId}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-semibold text-green-600">
                    {order.totalAmount}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-600">{order.orderDate}</div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {orders.length === 0 && (
        <div className="px-6 py-8 text-center">
          <div className="text-gray-400 text-sm">
            No orders found for this customer
          </div>
        </div>
      )}
    </div>
  );
};

const DocumentViewer = ({ document }: { document: DocumentResponse }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">
          {document.documentName}
        </h3>
        <p className="text-purple-100 text-sm mt-1">
          Document ID: {document.documentId}
        </p>
      </div>
      <div className="relative">
        <div
          className={`px-6 py-6 transition-all duration-300 ease-in-out overflow-hidden ${
            isExpanded ? "max-h-none" : "max-h-[200px]"
          }`}
        >
          <div className="prose prose-gray max-w-none">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-semibold text-gray-800 mt-5 mb-3">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-medium text-gray-700 mt-4 mb-2">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-700 mb-3 leading-relaxed">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside mb-4 space-y-1 text-gray-700">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside mb-4 space-y-1 text-gray-700">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-gray-700 ml-2">{children}</li>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">
                    {children}
                  </strong>
                ),
                em: ({ children }) => (
                  <em className="italic text-gray-700">{children}</em>
                ),
                code: ({ children }) => (
                  <code className="bg-gray-100 text-purple-600 px-1.5 py-0.5 rounded text-sm font-mono">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 overflow-x-auto mb-4">
                    {children}
                  </pre>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-purple-500 pl-4 italic text-gray-600 mb-4">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {document.documentContent}
            </ReactMarkdown>
          </div>
        </div>

        {/* Gradient overlay when collapsed */}
        {!isExpanded && (
          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent pointer-events-none" />
        )}

        {/* Expand/Collapse button */}
        <div className="px-6 pb-4">
          <button
            onClick={toggleExpanded}
            className="w-full flex items-center justify-center space-x-2 py-2 px-4 text-sm font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors duration-200 border border-purple-200"
          >
            <span>{isExpanded ? "Show less" : "Show more"}</span>
            <svg
              className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
