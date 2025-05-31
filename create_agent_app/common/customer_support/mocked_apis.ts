import * as fs from "fs";
import * as path from "path";

export type OrderSummaryResponse = {
  orderId: string;
  items: string[];
  totalAmount: number;
  orderDate: string;
};

export type OrderStatusResponse = {
  orderId: string;
  status: "pending" | "shipped" | "delivered" | "cancelled";
};

export type DocumentResponse = {
  documentId: string;
  documentName: string;
  documentContent: string;
};

const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export const httpGETCustomerOrderHistory = (): OrderSummaryResponse[] => {
  return [
    {
      orderId: "9127412",
      items: ["iPhone 14 Pro"],
      totalAmount: 959,
      orderDate: "2024-02-05",
    },
    {
      orderId: "3451323",
      items: ["Airpods Pro"],
      totalAmount: 299,
      orderDate: "2024-01-15",
    },
  ];
};

export const httpGETOrderStatus = async (
  orderId: string
): Promise<OrderStatusResponse> => {
  if (!["9127412", "3451323"].includes(orderId)) {
    throw new Error("Order not found");
  }

  await sleep(100);
  const statuses: ("pending" | "shipped" | "delivered" | "cancelled")[] = [
    "pending",
    "shipped",
    "delivered",
    "cancelled",
  ];
  const randomIndex = Math.floor(Math.random() * statuses.length);
  const randomStatus = statuses[randomIndex]!;

  return {
    orderId,
    status: randomStatus,
  };
};

export const httpGETCompanyPolicy = async (): Promise<DocumentResponse> => {
  await sleep(100);

  const filePath = getKnowledgeBasePath("company_policy.md");
  const documentContent = fs.readFileSync(filePath, "utf-8");

  return {
    documentId: "company_policy",
    documentName: "Company Policy",
    documentContent: documentContent,
  };
};

export const httpGETTroubleshootingGuide = async (
  guide: "internet" | "mobile" | "television" | "ecommerce"
): Promise<DocumentResponse> => {
  await sleep(100);

  const filePath = getKnowledgeBasePath(`troubleshooting_${guide}.md`);
  const documentContent = fs.readFileSync(filePath, "utf-8");

  return {
    documentId: `troubleshooting_${guide}`,
    documentName: `Troubleshooting ${guide}`,
    documentContent: documentContent,
  };
};

const findPackageRoot = (): string => {
  let currentDir = __dirname;
  while (currentDir !== path.dirname(currentDir)) {
    if (fs.existsSync(path.join(currentDir, "package.json"))) {
      return currentDir;
    }
    currentDir = path.dirname(currentDir);
  }
  throw new Error("Could not find package root");
};

const getKnowledgeBasePath = (filename: string): string => {
  const packageRoot = findPackageRoot();
  return path.join(
    packageRoot,
    "common",
    "customer_support",
    "knowledge_base",
    filename
  );
};
